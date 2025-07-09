from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from .models import Lead, db

leads = Blueprint('leads', __name__)

SEGMENTOS = ['Tecnologia', 'Saúde', 'Educação', 'Varejo', 'Serviços', 'Indústria', 'Agronegócio', 'Financeiro', 'Imobiliário', 'Outros']
STATUS_LEADS = ['NOVO_LEAD', 'CONTATADO', 'AGENDADO', 'PROPOSTA_ENVIADA', 'FECHADO', 'SEM_INTERESSE', 'PROPOSTA_REJEITADA']

@leads.route('/leads')
@login_required
def list_leads():
    return render_template('leads.html')

@leads.route('/novo-lead')
@login_required
def new_lead_form():
    return render_template('novo_lead.html')

@leads.route('/api/config', methods=['GET'])
@login_required
def get_config():
    return jsonify({'success': True, 'segmentos': SEGMENTOS, 'status_leads': STATUS_LEADS})

@leads.route('/api/leads/check_duplicates', methods=['GET'])
@login_required
def check_duplicates():
    search_term = request.args.get('term', '')
    if not search_term or len(search_term) < 3:
        return jsonify({'success': True, 'duplicates': []})
    duplicates = Lead.query.filter(Lead.nome_conta.ilike(f'%{search_term}%')).all()
    return jsonify({'success': True, 'duplicates': [lead.to_dict() for lead in duplicates]})

@leads.route('/api/leads', methods=['GET'])
@login_required
def get_leads():
    try:
        query = Lead.query.filter_by(user_id=current_user.id)
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
        tipo_conta=data.get('tipo_conta', 'Privada'), # Salva o novo campo
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

@leads.route('/api/leads/<int:lead_id>', methods=['GET'])
@login_required
def get_lead_details(lead_id):
    lead = Lead.query.filter_by(id=lead_id, user_id=current_user.id).first_or_404()
    return jsonify({'success': True, 'lead': lead.to_dict()})

@leads.route('/api/leads/<int:lead_id>', methods=['PUT'])
@login_required
def update_lead(lead_id):
    lead = Lead.query.filter_by(id=lead_id, user_id=current_user.id).first_or_404()
    data = request.get_json()
    
    lead.tipo_conta = data.get('tipo_conta', lead.tipo_conta) # Atualiza o novo campo
    lead.nome_completo = data.get('nome_completo', lead.nome_completo)
    lead.nome_conta = data.get('nome_conta', lead.nome_conta)
    lead.email = data.get('email', lead.email)
    lead.telefone_celular = data.get('telefone_celular', lead.telefone_celular)
    lead.telefone_fixo = data.get('telefone_fixo', lead.telefone_fixo)
    lead.segmento = data.get('segmento', lead.segmento)
    lead.status_lead = data.get('status_lead', lead.status_lead)
    lead.observacoes = data.get('observacoes', lead.observacoes)
    
    db.session.commit()
    return jsonify({'success': True, 'message': 'Lead atualizado com sucesso!'})

@leads.route('/api/leads/<int:lead_id>', methods=['DELETE'])
@login_required
def delete_lead(lead_id):
    lead = Lead.query.filter_by(id=lead_id, user_id=current_user.id).first_or_404()
    db.session.delete(lead)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Lead excluído com sucesso!'})