from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from .models import Lead, User, db, Conta, HistoricoAlteracao
from .config_constants import ESTAGIOS_CICLO_VIDA, STATUS_LEADS, TEMPERATURAS
from datetime import datetime

leads = Blueprint('leads', __name__)

# --- ROTA DE PÁGINA ---
@leads.route('/leads')
@login_required
def listar_leads():
    """Renderiza a página principal de gestão de leads."""
    return render_template('leads/leads.html')

# --- ROTAS DE API ---
@leads.route('/api/leads/config', methods=['GET'])
@login_required
def get_leads_config():
    """Fornece as opções para os filtros da página de leads."""
    return jsonify({
        'success': True,
        'estagios': ESTAGIOS_CICLO_VIDA,
        'status': STATUS_LEADS,
        'temperaturas': TEMPERATURAS
    })

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

# --- ADIÇÃO v6.0: Rota para assumir um lead do pool ---
@leads.route('/api/leads/<int:lead_id>/assumir', methods=['POST'])
@login_required
def assumir_lead(lead_id):
    lead = Lead.query.get_or_404(lead_id)
    conta = Conta.query.get_or_404(lead.conta_id)

    if lead.user_id is not None:
        return jsonify({'success': False, 'error': f'Este lead já foi assumido por {lead.owner.name}.'}), 409

    lead.user_id = current_user.id
    if conta.user_id is None:
        conta.user_id = current_user.id
    conta.user_id = current_user.id # Atribui a conta também
    lead.status_lead = 'Tentando Contato'
    lead.data_apropriacao = datetime.utcnow()
    lead.data_ultima_atualizacao = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Lead assumido com sucesso!'})

# --- ADIÇÃO v6.0: Rota para criar um novo lead (oportunidade) para uma conta existente ---
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