from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import Conta, Contato, Lead, User, db, HistoricoAlteracao
from .utils import is_valid_cnpj, get_cnpj_hash, normalize_name

contas = Blueprint('contas', __name__)

SEGMENTOS = ['Tecnologia', 'Saúde', 'Educação', 'Varejo', 'Serviços', 'Indústria', 'Agronegócio', 'Financeiro', 'Imobiliário', 'Outros']
STATUS_LEADS = ['NOVO_LEAD', 'CONTATADO', 'AGENDADO', 'PROPOSTA_ENVIADA', 'FECHADO', 'SEM_INTERESSE', 'PROPOSTA_REJEITADA']

# --- Função Auxiliar para Checagem de Permissão ---
def check_permission(conta):
    """Verifica se o usuário atual tem permissão para acessar/modificar uma conta."""
    if current_user.has_role('admin') or conta.user_id == current_user.id:
        return True
    if current_user.has_role('gerente'):
        liderados_ids = [liderado.id for liderado in current_user.liderados]
        if conta.user_id in liderados_ids:
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
    if not check_permission(conta):
        flash("Você não tem permissão para ver esta conta.", "danger")
        return redirect(url_for('contas.listar_contas'))
    return render_template('contas/detalhe_conta.html', conta=conta)

# --- ROTAS DE API ---

@contas.route('/api/contas', methods=['GET'])
@login_required
def get_contas():
    # --- ALTERAÇÃO v4.01: Lógica de Paginação ---
    page = request.args.get('page', 1, type=int)
    per_page = 15 # Itens por página
    
    query = Conta.query.filter_by(is_active=True)
    
    if current_user.has_role('gerente'):
        liderados_ids = [liderado.id for liderado in current_user.liderados]
        liderados_ids.append(current_user.id)
        query = query.filter(Conta.user_id.in_(liderados_ids))
    elif not current_user.has_role('admin'):
        query = query.filter_by(user_id=current_user.id)
    
    if current_user.has_role('admin'):
        owner_id = request.args.get('owner_id')
        if owner_id: query = query.filter_by(user_id=owner_id)

    search = request.args.get('search', '').strip()
    if search: query = query.filter(db.or_(Conta.nome_fantasia.ilike(f'%{search}%'), Conta.razao_social.ilike(f'%{search}%')))
    
    segmento = request.args.get('segmento', '').strip()
    if segmento: query = query.filter(Conta.segmento == segmento)
    
    # --- ALTERAÇÃO v4.01: Usando .paginate() em vez de .all() ---
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
    if not check_permission(conta):
        return jsonify({'success': False, 'error': 'Você não tem permissão para editar esta conta.'}), 403
    
    data = request.get_json()
    
    # --- ADIÇÃO v4.02: Lógica para registrar o histórico de alterações ---
    changes = []
    
    if 'cnpj' in data and data.get('cnpj') and data.get('cnpj') != conta.cnpj:
        if not is_valid_cnpj(data['cnpj']): return jsonify({'success': False, 'error': 'O CNPJ fornecido é inválido.'}), 400
        cnpj_hash = get_cnpj_hash(data['cnpj'])
        existing_conta = Conta.query.filter(Conta.id != conta_id, Conta.cnpj_hash == cnpj_hash).first()
        if existing_conta: return jsonify({'success': False, 'error': f'Este CNPJ já pertence à conta "{existing_conta.nome_fantasia}".'}), 409
        changes.append({'campo': 'CNPJ', 'valor_antigo': conta.cnpj, 'valor_novo': data['cnpj']})
        conta.cnpj = data['cnpj']

    # Compara cada campo e registra a alteração se houver diferença
    if data.get('nome_fantasia') and data['nome_fantasia'] != conta.nome_fantasia:
        changes.append({'campo': 'Nome Fantasia', 'valor_antigo': conta.nome_fantasia, 'valor_novo': data['nome_fantasia']})
        conta.nome_fantasia = data['nome_fantasia']
    else:
        conta.nome_fantasia = data.get('nome_fantasia', conta.nome_fantasia)
        
    if data.get('razao_social') and data['razao_social'] != conta.razao_social:
        changes.append({'campo': 'Razão Social', 'valor_antigo': conta.razao_social, 'valor_novo': data['razao_social']})
        conta.razao_social = data['razao_social']
    else:
        conta.razao_social = data.get('razao_social', conta.razao_social)

    if data.get('segmento') and data['segmento'] != conta.segmento:
        changes.append({'campo': 'Segmento', 'valor_antigo': conta.segmento, 'valor_novo': data['segmento']})
        conta.segmento = data['segmento']
    else:
        conta.segmento = data.get('segmento', conta.segmento)

    if data.get('tipo_conta') and data['tipo_conta'] != conta.tipo_conta:
        changes.append({'campo': 'Tipo Conta', 'valor_antigo': conta.tipo_conta, 'valor_novo': data['tipo_conta']})
        conta.tipo_conta = data['tipo_conta']
    else:
        conta.tipo_conta = data.get('tipo_conta', conta.tipo_conta)
    
    if 'matriz_id' in data:
        matriz_id = data.get('matriz_id')
        nova_matriz_id = int(matriz_id) if matriz_id and int(matriz_id) != conta.id else None
        if nova_matriz_id != conta.matriz_id:
            changes.append({'campo': 'Matriz ID', 'valor_antigo': str(conta.matriz_id) if conta.matriz_id else 'Nenhuma', 'valor_novo': str(nova_matriz_id) if nova_matriz_id else 'Nenhuma'})
        conta.matriz_id = nova_matriz_id

    if current_user.has_role('admin') and 'owner_id' in data and data.get('owner_id') and int(data['owner_id']) != conta.user_id:
        owner_antigo = User.query.get(conta.user_id).name
        owner_novo = User.query.get(int(data['owner_id'])).name
        changes.append({'campo': 'Responsável', 'valor_antigo': owner_antigo, 'valor_novo': owner_novo})
        conta.user_id = int(data['owner_id'])
        
    # Salva as alterações na conta
    db.session.commit()

    # Cria os registros de histórico para cada alteração
    for change in changes:
        historico = HistoricoAlteracao(
            user_id=current_user.id,
            conta_id=conta.id,
            campo=change['campo'],
            valor_antigo=change['valor_antigo'],
            valor_novo=change['valor_novo']
        )
        db.session.add(historico)
    
    if changes:
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

# --- ADIÇÃO v4.02: Rota para buscar o histórico de uma conta ---
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