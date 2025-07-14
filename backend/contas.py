from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import Conta, Contato, Lead, User, db
from .utils import is_valid_cnpj, get_cnpj_hash, normalize_name

contas = Blueprint('contas', __name__)

SEGMENTOS = ['Tecnologia', 'Saúde', 'Educação', 'Varejo', 'Serviços', 'Indústria', 'Agronegócio', 'Financeiro', 'Imobiliário', 'Outros']
STATUS_LEADS = ['NOVO_LEAD', 'CONTATADO', 'AGENDADO', 'PROPOSTA_ENVIADA', 'FECHADO', 'SEM_INTERESSE', 'PROPOSTA_REJEITADA']

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
    query = Conta.query.filter_by(id=conta_id)
    if not current_user.has_role('admin'):
        liderados_ids = [liderado.id for liderado in current_user.liderados]
        liderados_ids.append(current_user.id)
        if not (current_user.has_role('gerente') and conta.user_id in liderados_ids):
             query = query.filter_by(user_id=current_user.id)
    conta = query.first_or_404()
    return render_template('contas/detalhe_conta.html', conta=conta)

# --- ROTAS DE API ---

@contas.route('/api/contas', methods=['GET'])
@login_required
def get_contas():
    query = Conta.query
    
    # --- ALTERAÇÃO: Implementada a lógica de visualização por papel ---
    if current_user.has_role('gerente'):
        # Gerente vê as suas contas e as de seus liderados
        liderados_ids = [liderado.id for liderado in current_user.liderados]
        liderados_ids.append(current_user.id) # Inclui o próprio gerente
        query = query.filter(Conta.user_id.in_(liderados_ids))
    elif not current_user.has_role('admin'):
        # Vendedor vê apenas as suas
        query = query.filter_by(user_id=current_user.id)
    
    # Filtro de vendedor (usado apenas por admins)
    if current_user.has_role('admin'):
        owner_id = request.args.get('owner_id')
        if owner_id: query = query.filter_by(user_id=owner_id)

    search = request.args.get('search', '').strip()
    if search: query = query.filter(db.or_(Conta.nome_fantasia.ilike(f'%{search}%'), Conta.razao_social.ilike(f'%{search}%')))
    
    segmento = request.args.get('segmento', '').strip()
    if segmento: query = query.filter(Conta.segmento == segmento)
    
    contas_list = [c.to_dict() for c in query.order_by(Conta.nome_fantasia).all()]
    return jsonify({'success': True, 'contas': contas_list})

@contas.route('/api/contas/<int:conta_id>', methods=['PUT'])
@login_required
def update_conta(conta_id):
    query = Conta.query.filter_by(id=conta_id)
    if not current_user.has_role('admin'):
        liderados_ids = [liderado.id for liderado in current_user.liderados]
        liderados_ids.append(current_user.id)
        conta_para_verificar = query.first()
        if not (current_user.has_role('gerente') and conta_para_verificar and conta_para_verificar.user_id in liderados_ids):
             query = query.filter_by(user_id=current_user.id)
    conta = query.first_or_404("Conta não encontrada ou você não tem permissão para editá-la.")
    data = request.get_json()

    if 'cnpj' in data and data.get('cnpj') and data.get('cnpj') != conta.cnpj:
        if not is_valid_cnpj(data['cnpj']): return jsonify({'success': False, 'error': 'O CNPJ fornecido é inválido.'}), 400
        cnpj_hash = get_cnpj_hash(data['cnpj'])
        existing_conta = Conta.query.filter(Conta.id != conta_id, Conta.cnpj_hash == cnpj_hash).first()
        if existing_conta: return jsonify({'success': False, 'error': f'Este CNPJ já pertence à conta "{existing_conta.nome_fantasia}".'}), 409
        conta.cnpj = data['cnpj']

    conta.nome_fantasia = data.get('nome_fantasia', conta.nome_fantasia)
    conta.razao_social = data.get('razao_social', conta.razao_social)
    conta.segmento = data.get('segmento', conta.segmento)
    conta.tipo_conta = data.get('tipo_conta', conta.tipo_conta)
    
    # Todos os usuários podem editar a matriz
    if current_user.has_role('admin'):
        if 'owner_id' in data and data.get('owner_id'): conta.user_id = int(data['owner_id'])
    if 'matriz_id' in data:
        matriz_id = data['matriz_id']
        conta.matriz_id = int(matriz_id) if matriz_id and int(matriz_id) != conta.id else None
        
    db.session.commit()
    return jsonify({'success': True, 'message': 'Conta atualizada com sucesso!'})

# --- ADIÇÃO: Nova rota para desativar (soft delete) uma conta ---
@contas.route('/api/contas/<int:conta_id>', methods=['DELETE'])
@login_required
def desativar_conta(conta_id):
    query = Conta.query.filter_by(id=conta_id)
    if not current_user.has_role('admin'):
        query = query.filter_by(user_id=current_user.id)
    conta = query.first_or_404("Conta não encontrada ou você não tem permissão para esta ação.")

    # Lógica para tratar filiais órfãs
    for filial in conta.filiais:
        filial.matriz_id = None
    
    conta.is_active = False
    db.session.commit()
    
    flash(f"A conta '{conta.nome_fantasia}' foi desativada.", "success")
    return jsonify({'success': True, 'message': 'Conta desativada.'})

@contas.route('/api/admin/form_data', methods=['GET'])
@login_required
def get_admin_form_data():
    if not current_user.has_role('admin'): return jsonify({'success': False, 'error': 'Acesso não autorizado'}), 403
    vendedores = User.query.filter_by(is_active=True).all()
    contas = Conta.query.filter_by(is_active=True).order_by(Conta.nome_fantasia).all()
    return jsonify({'success': True, 'vendedores': [{'id': v.id, 'name': v.name} for v in vendedores], 'contas': [{'id': c.id, 'nome_fantasia': c.nome_fantasia} for c in contas]})

@contas.route('/api/contas/<int:conta_id>/details')
@login_required
def get_conta_details(conta_id):
    query = Conta.query.filter_by(id=conta_id)
    if not current_user.has_role('admin'): query = query.filter_by(user_id=current_user.id)
    conta = query.first_or_404()
    
    # --- ALTERAÇÃO V2.07: Busca apenas contatos ativos ---
    contatos_ativos = conta.contatos.filter_by(is_active=True).all()
    
    return jsonify({'success': True, 'conta': conta.to_dict(), 'contatos': [c.to_dict() for c in contatos_ativos], 'leads': [l.to_dict() for l in conta.leads.all()]})

@contas.route('/api/contas/<int:conta_id>/contatos', methods=['POST'])
@login_required
def adicionar_contato(conta_id):
    query = Conta.query.filter_by(id=conta_id)
    if not current_user.has_role('admin'): query = query.filter_by(user_id=current_user.id)
    conta = query.first_or_404()
    
    data = request.get_json()
    if not data or not data.get('nome'): return jsonify({'success': False, 'error': 'O nome do contato é obrigatório.'}), 400
    novo_contato = Contato(conta_id=conta.id, nome=data['nome'], email=data.get('email'), telefone=data.get('telefone'), cargo=data.get('cargo'))
    db.session.add(novo_contato)
    db.session.commit()
    return jsonify({'success': True, 'contato': novo_contato.to_dict()})

# --- ADIÇÃO V2.07: Rota para editar um contato específico ---
@contas.route('/api/contatos/<int:contato_id>', methods=['PUT'])
@login_required
def update_contato(contato_id):
    contato = Contato.query.get_or_404(contato_id)
    conta = Conta.query.filter_by(id=contato.conta_id)
    if not current_user.has_role('admin'):
        conta = conta.filter_by(user_id=current_user.id)
    conta.first_or_404("Você não tem permissão para editar este contato.")
    data = request.get_json()
    contato.nome = data.get('nome', contato.nome)
    contato.email = data.get('email', contato.email)
    contato.telefone = data.get('telefone', contato.telefone)
    contato.cargo = data.get('cargo', contato.cargo)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Contato atualizado.'})

# --- ADIÇÃO V2.07: Rota para desativar (soft delete) um contato ---
@contas.route('/api/contatos/<int:contato_id>', methods=['DELETE'])
@login_required
def delete_contato(contato_id):
    contato = Contato.query.get_or_404(contato_id)
    conta = Conta.query.filter_by(id=contato.conta_id)
    if not current_user.has_role('admin'):
        conta = conta.filter_by(user_id=current_user.id)
    conta.first_or_404("Você não tem permissão para excluir este contato.")
    contato.is_active = False
    db.session.commit()
    return jsonify({'success': True, 'message': 'Contato desativado.'})

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
        novo_lead = Lead(conta_id=nova_conta.id, user_id=current_user.id, contato_id=novo_contato.id if novo_contato else None, titulo=data.get('lead_titulo'), valor_estimado=data.get('lead_valor') or None)
        db.session.add(novo_lead)
    
    db.session.commit()
    flash('Conta criada com sucesso!', 'success')
    return jsonify({'success': True, 'redirect_url': url_for('contas.listar_contas')})