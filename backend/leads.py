from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from .models import Lead, User, db, Conta, HistoricoAlteracao
from .config_constants import ESTAGIOS_CICLO_VIDA, TEMPERATURAS
from datetime import datetime
from .contas import check_permission

leads = Blueprint('leads', __name__)

# --- ROTA DE PÁGINA ---
@leads.route('/leads')
@login_required
def listar_leads():
    """Renderiza a página principal de gestão de leads."""
    return render_template('leads/leads.html')

# --- ROTAS DE API ---
# --- Rota para buscar as estatísticas de leads por status ---
@leads.route('/api/leads/stats', methods=['GET'])
@login_required
def get_lead_stats():
    """API que retorna a contagem de leads por status, respeitando as permissões."""
    view_mode = request.args.get('view_mode', 'meus_leads')
    
    if view_mode == 'pool':
        base_query = Lead.query.filter(Lead.user_id == None)
    else:
        base_query = Lead.query.filter(Lead.user_id != None)
        if current_user.has_role('gerente'):
            liderados_ids = [liderado.id for liderado in current_user.liderados]
            liderados_ids.append(current_user.id)
            base_query = base_query.filter(Lead.user_id.in_(liderados_ids))
        elif not current_user.has_role('admin'):
            base_query = base_query.filter(Lead.user_id == current_user.id)

    # --- Aplica o filtro da query base antes de agrupar ---
    stats_query = base_query.with_entities(Lead.status_lead, db.func.count(Lead.id)).group_by(Lead.status_lead).all()
    stats_dict = dict(stats_query)

    return jsonify({'success': True, 'stats': stats_dict})

@leads.route('/api/leads', methods=['GET'])
@login_required
def get_leads():
    """API para buscar, filtrar e paginar leads com base nas permissões do usuário."""
    page = request.args.get('page', 1, type=int)
    per_page = 15
    view_mode = request.args.get('view_mode', 'meus_leads')
    search = request.args.get('search', '').strip()
    estagio = request.args.get('estagio', '')
    status = request.args.get('status', '')
    temperatura = request.args.get('temperatura', '')
    follow_up = request.args.get('followup', type=lambda v: v.lower() == 'true')
    owner_id_str = request.args.get('owner_id')

    query = Lead.query.join(Conta)
    
    if view_mode == 'pool':
        query = query.filter(Lead.user_id == None)
    else:
        if current_user.has_role('gerente'):
            liderados_ids = [liderado.id for liderado in current_user.liderados]
            liderados_ids.append(current_user.id)
            query = query.filter(Lead.user_id.in_(liderados_ids))
        elif not current_user.has_role('admin'):
            query = query.filter(Lead.user_id == current_user.id)
    
    # --- Usa a variável correta e garante que o valor é um inteiro ---
    if (current_user.has_role('admin') or current_user.has_role('gerente')) and owner_id_str:
        try:
            owner_id = int(owner_id_str)
            query = query.filter(Lead.user_id == owner_id)
        except (ValueError, TypeError):
            pass # Ignora o filtro se o valor não for um número válido

    if search:
        query = query.filter(db.or_(Lead.titulo.ilike(f'%{search}%'), Conta.nome_fantasia.ilike(f'%{search}%')))
    if estagio:
        query = query.filter(Lead.estagio_ciclo_vida == estagio)
    if status:
        query = query.filter(Lead.status_lead == status)
    if temperatura:
        query = query.filter(Lead.temperatura == temperatura)
    if follow_up:
        query = query.filter(Lead.follow_up_necessario == True)

    pagination = query.order_by(Lead.data_ultima_atualizacao.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    leads_list = []
    for lead in pagination.items:
        lead_dict = lead.to_dict()
        lead_dict['conta_nome'] = lead.conta.nome_fantasia
        lead_dict['conta_id'] = lead.conta_id
        if lead.user_id and lead.owner:
            lead_dict['owner_name'] = lead.owner.name
        else:
            lead_dict['owner_name'] = 'Disponível (Pool)'
        leads_list.append(lead_dict)
    
    return jsonify({
        'success': True,
        'leads': leads_list,
        'pagination': {
            'total': pagination.total, 'pages': pagination.pages, 'has_prev': pagination.has_prev,
            'has_next': pagination.has_next, 'page': pagination.page
        }
    })

# --- Lógica de "Assumir Lead" corrigida ---
@leads.route('/api/leads/<int:lead_id>/assumir', methods=['POST'])
@login_required
def assumir_lead(lead_id):
    lead = Lead.query.get_or_404(lead_id)
    conta = Conta.query.get_or_404(lead.conta_id)

    if lead.user_id is not None:
        return jsonify({'success': False, 'error': f'Este lead já foi assumido por {lead.owner.name}.'}), 409

    # 1. Atribui a conta ao usuário, se ela estiver no pool
    if conta.user_id is None:
        conta.user_id = current_user.id

    # 2. Atribui o lead clicado e todos os outros leads órfãos da mesma conta
    leads_orfans_da_conta = Lead.query.filter_by(conta_id=conta.id, user_id=None).all()
    for l in leads_orfans_da_conta:
        l.user_id = current_user.id
        l.status_lead = 'Tentando Contato'
        l.data_apropriacao = datetime.utcnow()
        l.data_ultima_atualizacao = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Lead e conta assumidos com sucesso!'})

# --- Lógica de "Reatribuir Lead" corrigida para usar check_permission na Conta pai ---
@leads.route('/api/leads/<int:lead_id>/reatribuir', methods=['POST'])
@login_required
def reatribuir_lead(lead_id):
    lead = Lead.query.get_or_404(lead_id)
    conta = Conta.query.get_or_404(lead.conta_id)
    data = request.get_json()
    novo_owner_id = data.get('new_owner_id')

    if not novo_owner_id:
        return jsonify({'success': False, 'error': 'Novo responsável não especificado.'}), 400

    # A permissão para reatribuir um lead é a mesma de editar a CONTA pai.
    if not check_permission(conta, for_editing=True):
        return jsonify({'success': False, 'error': 'Você não tem permissão para reatribuir leads desta conta.'}), 403

    owner_antigo_nome = lead.owner.name if lead.owner else "Ninguém (Pool)"
    novo_owner = User.query.get_or_404(novo_owner_id)

    # Altera APENAS o dono do Lead, não da conta.
    lead.user_id = novo_owner_id
    lead.data_ultima_atualizacao = datetime.utcnow()
    
    # Log de auditoria para o Lead
    historico_lead = HistoricoAlteracao(
        user_id=current_user.id, lead_id=lead.id, campo='Responsável (Oportunidade)',
        valor_antigo=owner_antigo_nome, valor_novo=novo_owner.name
    )
    db.session.add(historico_lead)
    db.session.commit()
    
    # Lógica de notificação (a ser implementada)
    # Ex: criar_notificacao(novo_owner_id, f"O lead {lead.titulo} foi atribuído a você.")

    return jsonify({'success': True, 'message': 'Oportunidade reatribuída com sucesso.'})

# --- Rota para criar um novo lead (oportunidade) para uma conta existente ---
@leads.route('/api/leads', methods=['POST'])
@login_required
def criar_lead():
    data = request.get_json()
    conta_id = data.get('conta_id')
    titulo = data.get('titulo')
    if not conta_id or not titulo:
        return jsonify({'success': False, 'error': 'Conta e Título são obrigatórios.'}), 400
    conta = Conta.query.get_or_404(conta_id)
    # A permissão para criar um lead é a mesma de ver a conta
    if not check_permission(conta):
         return jsonify({'success': False, 'error': 'Você não tem permissão para adicionar um lead a esta conta.'}), 403
    novo_lead = Lead(
        conta_id=conta_id,
        user_id=current_user.id,
        titulo=titulo,
        valor_estimado=data.get('valor_estimado') or None,
        contato_id=data.get('contato_id') or None,
        estagio_ciclo_vida='Lead',
        temperatura='Morno',
        status_lead='Novo'
    )
    db.session.add(novo_lead)
    db.session.commit()
    return jsonify({'success': True, 'lead': novo_lead.to_dict()})