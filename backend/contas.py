from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import Conta, Contato, Lead, db
from .utils import is_valid_cnpj, normalize_name

contas = Blueprint('contas', __name__)

@contas.route('/contas')
@login_required
def listar_contas():
    """Renderiza a página principal que lista todas as contas."""
    return render_template('contas/lista_contas.html')

@contas.route('/contas/nova')
@login_required
def nova_conta_form():
    """Renderiza o formulário para criar uma nova conta, contato e lead."""
    return render_template('contas/nova_conta.html')

# --- API Endpoints ---

@contas.route('/api/contas', methods=['GET'])
@login_required
def get_contas():
    """API que retorna a lista de contas para o frontend."""
    query = Conta.query.filter_by(user_id=current_user.id)
    # Adicionar lógica de filtros aqui no futuro
    
    contas_list = []
    for conta in query.order_by(Conta.nome_fantasia).all():
        contas_list.append({
            'id': conta.id,
            'nome_fantasia': conta.nome_fantasia,
            'razao_social': conta.razao_social,
            'cnpj': conta.cnpj,
            'tipo_conta': conta.tipo_conta,
            'owner_name': conta.owner.name
        })
    return jsonify({'success': True, 'contas': contas_list})


@contas.route('/api/contas', methods=['POST'])
@login_required
def criar_conta():
    """API para criar uma nova Conta, com o primeiro Contato e a primeira Oportunidade (Lead)."""
    data = request.get_json()

    # Validação dos dados
    if not data or not data.get('nome_fantasia'):
        return jsonify({'success': False, 'error': 'Nome Fantasia é obrigatório.'}), 400
    
    cnpj = data.get('cnpj')
    if cnpj and not is_valid_cnpj(cnpj):
        return jsonify({'success': False, 'error': 'O CNPJ fornecido é inválido.'}), 400

    # Verifica duplicidade pelo CNPJ, se fornecido
    if cnpj:
        existing_conta = Conta.query.filter_by(_cnpj=encrypt_data(cnpj)).first()
        if existing_conta:
            return jsonify({'success': False, 'error': f'Uma conta com este CNPJ já existe (ID: {existing_conta.id}).'}), 409

    # Cria a nova Conta
    nova_conta = Conta(
        user_id=current_user.id,
        nome_fantasia=data['nome_fantasia'],
        razao_social=data.get('razao_social'),
        cnpj=cnpj,
        tipo_conta=data.get('tipo_conta', 'Privada')
    )
    db.session.add(nova_conta)
    db.session.commit() # Commit para que a nova_conta tenha um ID

    # Cria o primeiro Contato associado
    if data.get('contato_nome'):
        novo_contato = Contato(
            conta_id=nova_conta.id,
            nome=data.get('contato_nome'),
            email=data.get('contato_email'),
            telefone=data.get('contato_telefone'),
            cargo=data.get('contato_cargo')
        )
        db.session.add(novo_contato)
        db.session.commit() # Commit para que o novo_contato tenha um ID

    # Cria a primeira Oportunidade (Lead) associada
    if data.get('lead_titulo'):
        novo_lead = Lead(
            conta_id=nova_conta.id,
            user_id=current_user.id,
            contato_id=novo_contato.id if 'novo_contato' in locals() else None,
            titulo=data.get('lead_titulo'),
            valor_estimado=data.get('lead_valor') or None
        )
        db.session.add(novo_lead)

    db.session.commit() # Commit final
    
    return jsonify({'success': True, 'message': 'Conta criada com sucesso!', 'conta_id': nova_conta.id}), 201