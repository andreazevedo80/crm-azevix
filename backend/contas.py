from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import Conta, Contato, Lead, User, db, HistoricoAlteracao
from .utils import is_valid_cnpj, get_cnpj_hash, normalize_name
from datetime import datetime
from .config_constants import SEGMENTOS, STATUS_LEADS

contas = Blueprint('contas', __name__)

# --- Função Auxiliar para Checagem de Permissão ---
def check_permission(conta, for_editing=False):
    """Verifica se o usuário atual tem permissão para uma conta."""
    if not conta: return False
    
    # Dono da conta e admin sempre têm permissão total
    if current_user.has_role('admin') or conta.user_id == current_user.id:
        return True
    
    # Gerente pode ver/editar contas de seus liderados
    if current_user.has_role('gerente'):
        liderados_ids = [liderado.id for liderado in current_user.liderados]
        if conta.user_id in liderados_ids:
            return True
            
    # Se a verificação for apenas para VISUALIZAÇÃO (não para edição)
    if not for_editing:
        # Vendedor pode ver uma conta se tiver pelo menos um lead nela
        user_leads_in_this_account = Lead.query.filter_by(conta_id=conta.id, user_id=current_user.id).count()
        if user_leads_in_this_account > 0:
            return True
            
    return False

# --- ROTAS DE PÁGINAS ---
@contas.route('/contas')
@login_required
def listar_contas():
    return render_template('contas/lista_contas.html')

@contas.route('/contas/nova')
@login_required
def nova_conta_form():
    return render_template('contas/nova_conta.html')

@contas.route('/contas/<int:conta_id>')
@login_required
def detalhe_conta(conta_id):
    conta = Conta.query.get_or_404(conta_id)
    if not check_permission(conta, for_editing=False):
        flash("Você não tem permissão para ver esta conta.", "danger")
        return redirect(url_for('contas.listar_contas'))
    return render_template('contas/detalhe_conta.html', conta=conta)

# --- ROTAS DE API ---

@contas.route('/api/contas', methods=['GET'])
@login_required
def get_contas():
    # --- Lógica de Paginação ---
    page = request.args.get('page', 1, type=int)
    per_page = 15 # Itens por página
    
    query = Conta.query.filter_by(is_active=True)
    
    if current_user.has_role('gerente'):
        liderados_ids = [liderado.id for liderado in current_user.liderados]
        liderados_ids.append(current_user.id)
        query = query.filter(Conta.user_id.in_(liderados_ids))
    elif not current_user.has_role('admin'):
        query = query.filter_by(user_id=current_user.id)
    
    if current_user.has_role('admin') or current_user.has_role('gerente'):
        owner_id = request.args.get('owner_id')
        if owner_id:
            query = query.filter(Conta.user_id == owner_id)

    search = request.args.get('search', '').strip()
    if search: query = query.filter(db.or_(Conta.nome_fantasia.ilike(f'%{search}%'), Conta.razao_social.ilike(f'%{search}%')))
    
    segmento = request.args.get('segmento', '').strip()
    if segmento: query = query.filter(Conta.segmento == segmento)
    
    # --- Usando .paginate() em vez de .all() ---
    pagination = query.order_by(Conta.nome_fantasia).paginate(page=page, per_page=per_page, error_out=False)
    contas_list = [c.to_dict() for c in pagination.items]
    
    return jsonify({
        'success': True,
        'contas': contas_list,
        'pagination': {
            'total': pagination.total,
            'pages': pagination.pages,
            'has_prev': pagination.has_prev,
            'has_next': pagination.has_next,
            'page': pagination.page
        }
    })

@contas.route('/api/contas/<int:conta_id>', methods=['PUT'])
@login_required
def update_conta(conta_id):
    conta = Conta.query.get_or_404(conta_id)
    if not check_permission(conta, for_editing=True):
        return jsonify({'success': False, 'error': 'Você não tem permissão para editar esta conta.'}), 403
    
    data = request.get_json()
    
    # --- CORREÇÃO: Lógica mais robusta para lidar com contas sem dono ---
    dados_antigos = {
        'Nome Fantasia': conta.nome_fantasia,
        'Razão Social': conta.razao_social,
        'Segmento': conta.segmento,
        'Tipo Conta': conta.tipo_conta,
        'Matriz': conta.matriz.nome_fantasia if conta.matriz else "Nenhuma",
        'Responsável': conta.owner.name if conta.owner else "Nenhum",
        'CNPJ': conta.cnpj
    }
    
    # Tratamento especial para CNPJ (mantendo a lógica original)
    if 'cnpj' in data and data.get('cnpj') and data.get('cnpj') != conta.cnpj:
        if not is_valid_cnpj(data['cnpj']): return jsonify({'success': False, 'error': 'O CNPJ fornecido é inválido.'}), 400
        cnpj_hash = get_cnpj_hash(data['cnpj'])
        existing_conta = Conta.query.filter(Conta.id != conta_id, Conta.cnpj_hash == cnpj_hash).first()
        if existing_conta: return jsonify({'success': False, 'error': f'Este CNPJ já pertence à conta "{existing_conta.nome_fantasia}".'}), 409
        dados_antigos['CNPJ'] = conta.cnpj
        conta.cnpj = data['cnpj']

    # Atualiza os campos
    conta.nome_fantasia = data.get('nome_fantasia', conta.nome_fantasia)
    conta.razao_social = data.get('razao_social', conta.razao_social)
    conta.segmento = data.get('segmento', conta.segmento)
    conta.tipo_conta = data.get('tipo_conta', conta.tipo_conta)
    
    if 'matriz_id' in data:
        matriz_id = data.get('matriz_id')
        conta.matriz_id = int(matriz_id) if matriz_id and int(matriz_id) != conta.id else None
        
    if 'owner_id' in data and data.get('owner_id'):
        novo_owner_id = int(data['owner_id'])
        # Validação de segurança: Gerente só pode atribuir para sua equipe
        if current_user.has_role('gerente') and not current_user.has_role('admin'):
            liderados_ids = [liderado.id for liderado in current_user.liderados]
            if novo_owner_id not in liderados_ids:
                return jsonify({'success': False, 'error': 'Você só pode atribuir contas para vendedores da sua equipe.'}), 403
        # Apenas admin ou gerente (que passou na validação) podem alterar
        if current_user.has_role('admin') or current_user.has_role('gerente'):
            conta.user_id = novo_owner_id
    
    # Compara e registra no histórico
    db.session.flush() # Aplica as mudanças à sessão para leitura
    
    changes_to_log = []
    if dados_antigos['Nome Fantasia'] != conta.nome_fantasia:
        changes_to_log.append({'campo': 'Nome Fantasia', 'valor_antigo': dados_antigos['Nome Fantasia'], 'valor_novo': conta.nome_fantasia})
    if dados_antigos['Razão Social'] != conta.razao_social:
        changes_to_log.append({'campo': 'Razão Social', 'valor_antigo': dados_antigos['Razão Social'], 'valor_novo': conta.razao_social})
    if dados_antigos['Segmento'] != conta.segmento:
        changes_to_log.append({'campo': 'Segmento', 'valor_antigo': dados_antigos['Segmento'], 'valor_novo': conta.segmento})
    if dados_antigos['Tipo Conta'] != conta.tipo_conta:
        changes_to_log.append({'campo': 'Tipo Conta', 'valor_antigo': dados_antigos['Tipo Conta'], 'valor_novo': conta.tipo_conta})
    if dados_antigos['Matriz'] != (conta.matriz.nome_fantasia if conta.matriz else "Nenhuma"):
        changes_to_log.append({'campo': 'Conta Matriz', 'valor_antigo': dados_antigos['Matriz'], 'valor_novo': (conta.matriz.nome_fantasia if conta.matriz else "Nenhuma")})
    if dados_antigos['Responsável'] != (conta.owner.name if conta.owner else "Nenhum"):
        changes_to_log.append({'campo': 'Responsável', 'valor_antigo': dados_antigos['Responsável'], 'valor_novo': (conta.owner.name if conta.owner else "Nenhum")})
    
    # Tratamento especial para CNPJ se foi alterado
    if 'CNPJ' in dados_antigos:
        changes_to_log.append({'campo': 'CNPJ', 'valor_antigo': dados_antigos['CNPJ'], 'valor_novo': conta.cnpj})

    for change in changes_to_log:
        historico = HistoricoAlteracao(
            user_id=current_user.id, conta_id=conta.id, campo=change['campo'],
            valor_antigo=change['valor_antigo'], valor_novo=change['valor_novo']
        )
        db.session.add(historico)
        
    db.session.commit()
    return jsonify({'success': True, 'message': 'Conta atualizada com sucesso!'})

@contas.route('/api/contas/<int:conta_id>', methods=['DELETE'])
@login_required
def desativar_conta(conta_id):
    conta = Conta.query.get_or_404(conta_id)
    if not check_permission(conta):
        return jsonify({'success': False, 'error': 'Você não tem permissão para esta ação.'}), 403

    for filial in conta.filiais:
        filial.matriz_id = None
    
    conta.is_active = False
    db.session.commit()
    
    flash(f"A conta '{conta.nome_fantasia}' foi desativada.", "success")
    return jsonify({'success': True, 'message': 'Conta desativada.'})

@contas.route('/api/admin/form_data', methods=['GET'])
@login_required
def get_admin_form_data():
    if not (current_user.has_role('admin') or current_user.has_role('gerente')):
        return jsonify({'success': False, 'error': 'Acesso não autorizado'}), 403
    
    if current_user.has_role('admin'):
        vendedores = User.query.filter_by(is_active=True).all()
    else: # Gerente
        vendedores = current_user.liderados.all()
    
    contas_list = Conta.query.filter_by(is_active=True).order_by(Conta.nome_fantasia).all()
    return jsonify({'success': True, 'vendedores': [{'id': v.id, 'name': v.name} for v in vendedores], 'contas': [{'id': c.id, 'nome_fantasia': c.nome_fantasia} for c in contas_list]})

@contas.route('/api/contas/<int:conta_id>/details')
@login_required
def get_conta_details(conta_id):
    conta = Conta.query.get_or_404(conta_id)
    if not check_permission(conta):
        return jsonify({'success': False, 'error': 'Acesso negado'}), 403
    
    contatos_ativos = conta.contatos.filter_by(is_active=True).all()
    return jsonify({'success': True, 'conta': conta.to_dict(), 'contatos': [c.to_dict() for c in contatos_ativos], 'leads': [l.to_dict() for l in conta.leads.all()]})

# --- Rota para buscar o histórico de uma conta ---
@contas.route('/api/contas/<int:conta_id>/historico', methods=['GET'])
@login_required
def get_conta_historico(conta_id):
    conta = Conta.query.get_or_404(conta_id)
    if not check_permission(conta):
        return jsonify({'success': False, 'error': 'Acesso negado'}), 403

    historico_query = HistoricoAlteracao.query.filter_by(conta_id=conta_id).order_by(HistoricoAlteracao.data_alteracao.desc()).all()
    
    historico_list = []
    for item in historico_query:
        user = User.query.get(item.user_id)
        historico_list.append({
            'data': item.data_alteracao.strftime('%d/%m/%Y %H:%M'),
            'usuario': user.name if user else 'Desconhecido',
            'campo': item.campo,
            'valor_antigo': item.valor_antigo,
            'valor_novo': item.valor_novo
        })

    return jsonify({'success': True, 'historico': historico_list})

@contas.route('/api/contas/<int:conta_id>/contatos', methods=['POST'])
@login_required
def adicionar_contato(conta_id):
    conta = Conta.query.get_or_404(conta_id)
    if not check_permission(conta):
        return jsonify({'success': False, 'error': 'Você não tem permissão para adicionar contatos a esta conta.'}), 403
    
    data = request.get_json()
    if not data or not data.get('nome'): return jsonify({'success': False, 'error': 'O nome do contato é obrigatório.'}), 400
    novo_contato = Contato(conta_id=conta.id, nome=data['nome'], email=data.get('email'), telefone=data.get('telefone'), cargo=data.get('cargo'))
    db.session.add(novo_contato)
    db.session.commit()
    return jsonify({'success': True, 'contato': novo_contato.to_dict()})

@contas.route('/api/contatos/<int:contato_id>', methods=['PUT'])
@login_required
def update_contato(contato_id):
    contato = Contato.query.get_or_404(contato_id)
    conta = Conta.query.get_or_404(contato.conta_id)
    if not check_permission(conta):
        return jsonify({'success': False, 'error': 'Você não tem permissão para editar este contato.'}), 403
    
    data = request.get_json()
    contato.nome = data.get('nome', contato.nome)
    contato.email = data.get('email', contato.email)
    contato.telefone = data.get('telefone', contato.telefone)
    contato.cargo = data.get('cargo', contato.cargo)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Contato atualizado.'})

@contas.route('/api/contatos/<int:contato_id>', methods=['DELETE'])
@login_required
def delete_contato(contato_id):
    contato = Contato.query.get_or_404(contato_id)
    conta = Conta.query.get_or_404(contato.conta_id)
    if not check_permission(conta):
        return jsonify({'success': False, 'error': 'Você não tem permissão para excluir este contato.'}), 403
    
    contato.is_active = False
    db.session.commit()
    return jsonify({'success': True, 'message': 'Contato desativado.'})

# --- ADIÇÃO v5.03: Rota dedicada para atualizar o processo de um Lead ---
@contas.route('/api/leads/<int:lead_id>/processo', methods=['PUT'])
@login_required
def update_lead_processo(lead_id):
    lead = Lead.query.get_or_404(lead_id)
    conta = Conta.query.get_or_404(lead.conta_id)
    if not check_permission(conta):
        return jsonify({'success': False, 'error': 'Você não tem permissão para editar este lead.'}), 403
        
    data = request.get_json()
    changes_to_log = []
    
    # Atualiza Status e verifica transições
    if 'status_lead' in data and data['status_lead'] != lead.status_lead:
        changes_to_log.append({'campo': 'Status', 'valor_antigo': lead.status_lead, 'valor_novo': data['status_lead']})
        lead.status_lead = data['status_lead']
        
        if lead.status_lead == 'Qualificado' and lead.estagio_ciclo_vida == 'Lead':
            changes_to_log.append({'campo': 'Estágio', 'valor_antigo': lead.estagio_ciclo_vida, 'valor_novo': 'Oportunidade'})
            lead.estagio_ciclo_vida = 'Oportunidade'
        elif lead.status_lead == 'Ganho' and lead.estagio_ciclo_vida != 'Cliente':
            changes_to_log.append({'campo': 'Estágio', 'valor_antigo': lead.estagio_ciclo_vida, 'valor_novo': 'Cliente'})
            lead.estagio_ciclo_vida = 'Cliente'

    if 'temperatura' in data and data['temperatura'] != lead.temperatura:
        changes_to_log.append({'campo': 'Temperatura', 'valor_antigo': lead.temperatura, 'valor_novo': data['temperatura']})
        lead.temperatura = data['temperatura']
        
    if 'follow_up_necessario' in data and data['follow_up_necessario'] != lead.follow_up_necessario:
        changes_to_log.append({'campo': 'Follow-up', 'valor_antigo': str(lead.follow_up_necessario), 'valor_novo': str(data['follow_up_necessario'])})
        lead.follow_up_necessario = data['follow_up_necessario']
        
    if 'motivo_perda' in data and data['motivo_perda'] != lead.motivo_perda:
        changes_to_log.append({'campo': 'Motivo da Perda', 'valor_antigo': lead.motivo_perda, 'valor_novo': data['motivo_perda']})
        lead.motivo_perda = data['motivo_perda']

    lead.data_ultima_atualizacao = datetime.utcnow()

    for change in changes_to_log:
        historico = HistoricoAlteracao(
            user_id=current_user.id, lead_id=lead.id, campo=change['campo'],
            valor_antigo=change['valor_antigo'], valor_novo=change['valor_novo']
        )
        db.session.add(historico)
        
    db.session.commit()
    return jsonify({'success': True, 'message': 'Processo do lead atualizado.'})

@contas.route('/api/contas/config', methods=['GET'])
@login_required
def get_contas_config():
    return jsonify({'success': True, 'segmentos': SEGMENTOS, 'status_leads': STATUS_LEADS})

@contas.route('/api/contas/search', methods=['GET'])
@login_required
def search_contas():
    term = request.args.get('term', '').strip()
    if len(term) < 3: return jsonify({'success': True, 'contas': []})
    normalized_term = normalize_name(term)
    query = Conta.query.filter(db.or_(Conta.nome_fantasia.ilike(f'%{normalized_term}%'), Conta.razao_social.ilike(f'%{normalized_term}%')))
    found_contas = [{'id': c.id, 'nome_fantasia': c.nome_fantasia, 'cnpj': c.cnpj, 'owner_name': c.owner.name} for c in query.limit(10).all()]
    return jsonify({'success': True, 'contas': found_contas})

@contas.route('/api/contas', methods=['POST'])
@login_required
def criar_conta():
    data = request.get_json()
    if not data or not data.get('nome_fantasia'): return jsonify({'success': False, 'error': 'Nome Fantasia é obrigatório.'}), 400
    cnpj = data.get('cnpj')
    if cnpj:
        if not is_valid_cnpj(cnpj): return jsonify({'success': False, 'error': 'O CNPJ fornecido é inválido.'}), 400
        cnpj_hash = get_cnpj_hash(cnpj)
        existing_conta = Conta.query.filter_by(cnpj_hash=cnpj_hash).first()
        if existing_conta: return jsonify({'success': False, 'error': f'Este CNPJ já está cadastrado para a conta "{existing_conta.nome_fantasia}", sob responsabilidade de {existing_conta.owner.name}.'}), 409
    
    matriz_id = data.get('matriz_id') if data.get('matriz_id') else None
    nova_conta = Conta(user_id=current_user.id, nome_fantasia=data['nome_fantasia'], razao_social=data.get('razao_social'), cnpj=cnpj, tipo_conta=data.get('tipo_conta', 'Privada'), segmento=data.get('segmento'), matriz_id=matriz_id)
    db.session.add(nova_conta)
    db.session.commit()
    
    novo_contato, novo_lead = None, None
    if data.get('contato_nome'):
        novo_contato = Contato(conta_id=nova_conta.id, nome=data.get('contato_nome'), email=data.get('contato_email'), telefone=data.get('contato_telefone'), cargo=data.get('contato_cargo'))
        db.session.add(novo_contato)
        db.session.commit()
    if data.get('lead_titulo'):
        # --- ALTERAÇÃO v5.03: Define os valores padrão para os novos campos do Lead ---
        novo_lead = Lead(
            conta_id=nova_conta.id, 
            user_id=current_user.id, 
            contato_id=novo_contato.id if novo_contato else None, 
            titulo=data.get('lead_titulo'), 
            valor_estimado=data.get('lead_valor') or None,
            estagio_ciclo_vida='Lead', # Valor Padrão
            temperatura='Morno', # Valor Padrão
            status_lead='Novo' # Novo status padrão
        )
        db.session.add(novo_lead)
    
    db.session.commit()
    flash('Conta criada com sucesso!', 'success')
    return jsonify({'success': True, 'redirect_url': url_for('contas.listar_contas')})