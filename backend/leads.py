from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from .models import Lead, HistoricoInteracao, db

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

@leads.route('/api/leads', methods=['GET'])
@login_required
def get_leads():
    query = Lead.query
    search = request.args.get('search')
    if search:
        query = query.filter(db.or_(
            Lead.nome_completo.ilike(f'%{search}%'),
            Lead.nome_conta.ilike(f'%{search}%'),
            Lead.email.ilike(f'%{search}%')
        ))
    
    leads_list = [lead.to_dict() for lead in query.order_by(Lead.data_ultima_atualizacao.desc()).all()]
    return jsonify({'success': True, 'leads': leads_list, 'total': len(leads_list)})

@leads.route('/api/leads', methods=['POST'])
@login_required
def create_lead():
    data = request.get_json()
    if not data or not data.get('nome_completo') or not data.get('nome_conta'):
        return jsonify({'success': False, 'error': 'Nome do contato e nome da empresa são obrigatórios.'}), 400

    new_lead = Lead(
        nome_completo=data['nome_completo'],
        nome_conta=data['nome_conta'],
        email=data.get('email'),
        telefone_celular=data.get('telefone_celular'),
        segmento=data.get('segmento'),
        observacoes=data.get('observacoes')
    )
    db.session.add(new_lead)
    db.session.commit()
    return jsonify({'success': True, 'lead': new_lead.to_dict()}), 201