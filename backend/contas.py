from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import Conta, Contato, Lead, db
from .utils import is_valid_cnpj, get_cnpj_hash, normalize_name

contas = Blueprint('contas', __name__)

SEGMENTOS = ['Tecnologia', 'Saúde', 'Educação', 'Varejo', 'Serviços', 'Indústria', 'Agronegócio', 'Financeiro', 'Imobiliário', 'Outros']

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
    """Renderiza a página de detalhes de uma conta específica."""
    conta = Conta.query.filter_by(id=conta_id, user_id=current_user.id).first_or_404()
    return render_template('contas/detalhe_conta.html', conta=conta)

# --- ROTAS DE API ---

@contas.route('/api/contas/<int:conta_id>/details')
@login_required
def get_conta_details(conta_id):
    """API que retorna todos os detalhes de uma conta (contatos, leads)."""
    conta = Conta.query.filter_by(id=conta_id, user_id=current_user.id).first_or_404()
    
    conta_data = conta.to_dict()
    contatos_data = [c.to_dict() for c in conta.contatos.all()]
    leads_data = [l.to_dict() for l in conta.leads.all()]

    return jsonify({'success': True, 'conta': conta_data, 'contatos': contatos_data, 'leads': leads_data})

@contas.route('/api/contas/<int:conta_id>/contatos', methods=['POST'])
@login_required
def adicionar_contato(conta_id):
    """API para adicionar um novo contato a uma conta existente."""
    conta = Conta.query.filter_by(id=conta_id, user_id=current_user.id).first_or_404()
    data = request.get_json()

    if not data or not data.get('nome'):
        return jsonify({'success': False, 'error': 'O nome do contato é obrigatório.'}), 400

    novo_contato = Contato(
        conta_id=conta.id,
        nome=data['nome'],
        email=data.get('email'),
        telefone=data.get('telefone'),
        cargo=data.get('cargo')
    )
    db.session.add(novo_contato)
    db.session.commit()
    return jsonify({'success': True, 'contato': novo_contato.to_dict()})

@contas.route('/api/contas/config', methods=['GET'])
@login_required
def get_contas_config():
    return jsonify({'success': True, 'segmentos': SEGMENTOS})

@contas.route('/api/contas/search', methods=['GET'])
@login_required
def search_contas():
    term = request.args.get('term', '').strip()
    if len(term) < 3: return jsonify({'success': True, 'contas': []})
    normalized_term = normalize_name(term)
    query = Conta.query.filter(Conta.nome_fantasia.ilike(f'%{normalized_term}%'))
    found_contas = [{'id': c.id, 'nome_fantasia': c.nome_fantasia, 'cnpj': c.cnpj, 'owner_name': c.owner.name} for c in query.limit(10).all()]
    return jsonify({'success': True, 'contas': found_contas})

@contas.route('/api/contas', methods=['GET'])
@login_required
def get_contas():
    query = Conta.query.filter_by(user_id=current_user.id).order_by(Conta.nome_fantasia)
    contas_list = [c.to_dict() for c in query.all()]
    return jsonify({'success': True, 'contas': contas_list})

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
    
    nova_conta = Conta(user_id=current_user.id, nome_fantasia=data['nome_fantasia'], razao_social=data.get('razao_social'), cnpj=cnpj, tipo_conta=data.get('tipo_conta', 'Privada'), segmento=data.get('segmento'))
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