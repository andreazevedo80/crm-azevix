from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from .models import Lead, db

leads = Blueprint('leads', __name__)

# --- Constantes de Configuração ---
SEGMENTOS = ['Tecnologia', 'Saúde', 'Educação', 'Varejo', 'Serviços', 'Indústria', 'Agronegócio', 'Financeiro', 'Imobiliário', 'Outros']
STATUS_LEADS = ['NOVO_LEAD', 'CONTATADO', 'AGENDADO', 'PROPOSTA_ENVIADA', 'FECHADO', 'SEM_INTERESSE']

# --- Rotas de Páginas ---

@leads.route('/leads')
@login_required
def list_leads():
    return render_template('leads.html')

@leads.route('/novo-lead')
@login_required
def new_lead_form():
    return render_template('novo_lead.html')

# --- Rotas de API ---

@leads.route('/api/config', methods=['GET'])
@login_required
def get_config():
    return jsonify({
        'success': True,
        'segmentos': SEGMENTOS,
        'status_leads': STATUS_LEADS
    })

@leads.route('/api/leads/check_duplicates', methods=['GET'])
@login_required
def check_duplicates():
    search_term = request.args.get('term', '')
    if not search_term or len(search_term) < 3:
        return jsonify({'success': True, 'duplicates': []})
    duplicates = Lead.query.filter(Lead.nome_conta.ilike(f'%{search_term}%')).all()
    return jsonify({
        'success': True,
        'duplicates': [lead.to_dict() for lead in duplicates]
    })

# --- ROTA PRINCIPAL CORRIGIDA ---
@leads.route('/api/leads', methods=['GET'])
@login_required
def get_leads():
    try:
        # 1. A query base AGORA filtra pelo ID do usuário logado.
        query = Lead.query.filter_by(user_id=current_user.id)

        # 2. Aplica os filtros adicionais sobre os leads do usuário.
        search = request.args.get('search', '').strip()
        status = request.args.get('status', '').strip()
        segmento = request.args.get('segmento', '').strip()

        if search:
            query = query.filter(db.or_(
                Lead.nome_completo.ilike(f'%{search}%'),
                Lead.nome_conta.ilike(f'%{search}%'),
                Lead.email.ilike(f'%{search}%')
            ))
        if status:
            query = query.filter(Lead.status_lead == status)
        if segmento:
            query = query.filter(Lead.segmento == segmento)
        
        leads_list = [lead.to_dict() for lead in query.order_by(Lead.data_ultima_atualizacao.desc()).all()]
        return jsonify({'success': True, 'leads': leads_list, 'total': len(leads_list)})
    except Exception as e:
        # Adiciona um log no terminal do Docker para facilitar o debug
        print(f"Erro na API get_leads: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@leads.route('/api/leads', methods=['POST'])
@login_required
def create_lead():
    data = request.get_json()
    if not data or not data.get('nome_completo') or not data.get('nome_conta'):
        return jsonify({'success': False, 'error': 'Nome do contato e nome da empresa são obrigatórios.'}), 400

    new_lead = Lead(
        user_id=current_user.id,
        nome_completo=data['nome_completo'],
        nome_conta=data['nome_conta'],
        email=data.get('email'),
        telefone_celular=data.get('telefone_celular'),
        telefone_fixo=data.get('telefone_fixo'),
        segmento=data.get('segmento'),
        observacoes=data.get('observacoes')
    )
    db.session.add(new_lead)
    db.session.commit()
    return jsonify({'success': True, 'lead': new_lead.to_dict()}), 201