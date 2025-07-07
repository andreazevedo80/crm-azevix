from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
from dotenv import load_dotenv
import os
import json
import urllib.parse # Importa para URL-encode, caso precise no futuro

# Carrega as variáveis do arquivo .env
load_dotenv()

app = Flask(__name__, 
            template_folder='../frontend/templates',
            static_folder='../frontend/static')

# Acessa as variáveis de ambiente carregadas pelo dotenv
DB_USER = os.getenv('POSTGRES_USER')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD')
DB_NAME = os.getenv('POSTGRES_DB')
DB_HOST = 'crm-azevix-db' 
DB_PORT = '5432'

# Para senhas SEM '@' e outros caracteres especiais que causam conflito em URLs:
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Para depuração, você pode imprimir a URL construída:
print(f"DEBUG: Constructed DATABASE_URL: {DATABASE_URL}")

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'crm-azevix-secret-key-2024'

# Inicializar extensões
db = SQLAlchemy(app)
CORS(app)

# Definir segmentos disponíveis
SEGMENTOS = [
    'Tecnologia', 'Saúde', 'Educação', 'Varejo', 'Serviços',
    'Indústria', 'Agronegócio', 'Financeiro', 'Imobiliário', 'Outros'
]

# Definir status dos leads
STATUS_LEADS = [
    'NOVO_LEAD', 'SEM_INTERESSE', 'INTERESSE_NAO_ATENDE', 'TELEFONE_INEXISTENTE',
    'EMAIL_APRESENTACAO_ENVIADO', 'CONTATADO', 'AGENDADO', 'PROPOSTA_ENVIADA', 'FECHADO'
]

# Modelo de dados para Leads
class Lead(db.Model):
    __tablename__ = 'leads'
    
    id = db.Column(db.Integer, primary_key=True)
    nome_completo = db.Column(db.String(200), nullable=False)
    nome_conta = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    telefone_fixo = db.Column(db.String(20))
    telefone_celular = db.Column(db.String(20))
    segmento = db.Column(db.String(50), nullable=False)
    status_lead = db.Column(db.String(50), nullable=False, default='NOVO_LEAD')
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    data_ultima_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    observacoes = db.Column(db.Text)
    
    historico_interacoes = db.relationship('HistoricoInteracao', backref='lead', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome_completo': self.nome_completo,
            'nome_conta': self.nome_conta,
            'email': self.email,
            'telefone_fixo': self.telefone_fixo,
            'telefone_celular': self.telefone_celular,
            'segmento': self.segmento,
            'status_lead': self.status_lead,
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None,
            'data_ultima_atualizacao': self.data_ultima_atualizacao.isoformat() if self.data_ultima_atualizacao else None,
            'observacoes': self.observacoes
        }

# Modelo de dados para Histórico de Interações
class HistoricoInteracao(db.Model):
    __tablename__ = 'historico_interacoes'
    
    id = db.Column(db.Integer, primary_key=True)
    lead_id = db.Column(db.Integer, db.ForeignKey('leads.id'), nullable=False)
    tipo_interacao = db.Column(db.String(50), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    data_interacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'lead_id': self.lead_id,
            'tipo_interacao': self.tipo_interacao,
            'descricao': self.descricao,
            'data_interacao': self.data_interacao.isoformat() if self.data_interacao else None
        }

# Rotas principais
@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/leads')
def leads():
    return render_template('leads.html')

@app.route('/novo-lead')
def novo_lead():
    return render_template('novo_lead.html')

# API Routes
@app.route('/api/leads', methods=['GET'])
def get_leads():
    try:
        search = request.args.get('search', '')
        status = request.args.get('status', '')
        segmento = request.args.get('segmento', '')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        query = Lead.query
        
        if search:
            query = query.filter(
                db.or_(
                    Lead.nome_completo.ilike(f'%{search}%'),
                    Lead.nome_conta.ilike(f'%{search}%'),
                    Lead.email.ilike(f'%{search}%')
                )
            )
        
        if status:
            query = query.filter(Lead.status_lead == status)
            
        if segmento:
            query = query.filter(Lead.segmento == segmento)
        
        query = query.order_by(Lead.data_ultima_atualizacao.desc())
        
        leads_paginated = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'success': True,
            'leads': [lead.to_dict() for lead in leads_paginated.items],
            'total': leads_paginated.total,
            'pages': leads_paginated.pages,
            'current_page': page,
            'per_page': per_page
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/leads', methods=['POST'])
def create_lead():
    try:
        data = request.get_json()
        
        required_fields = ['nome_completo', 'nome_conta', 'email', 'segmento']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'Campo {field} é obrigatório'}), 400
        
        lead = Lead(
            nome_completo=data['nome_completo'],
            nome_conta=data['nome_conta'],
            email=data['email'],
            telefone_fixo=data.get('telefone_fixo'),
            telefone_celular=data.get('telefone_celular'),
            segmento=data['segmento'],
            status_lead=data.get('status_lead', 'NOVO_LEAD'),
            observacoes=data.get('observacoes')
        )
        
        db.session.add(lead)
        db.session.commit()
        
        historico = HistoricoInteracao(
            lead_id=lead.id,
            tipo_interacao='OBSERVACAO',
            descricao='Lead cadastrado no sistema'
        )
        db.session.add(historico)
        db.session.commit()
        
        return jsonify({'success': True, 'lead': lead.to_dict()}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/leads/<int:lead_id>', methods=['PUT'])
def update_lead(lead_id):
    try:
        lead = Lead.query.get_or_404(lead_id)
        data = request.get_json()
        
        if 'nome_completo' in data:
            lead.nome_completo = data['nome_completo']
        if 'nome_conta' in data:
            lead.nome_conta = data['nome_conta']
        if 'email' in data:
            lead.email = data['email']
        if 'telefone_fixo' in data:
            lead.telefone_fixo = data['telefone_fixo']
        if 'telefone_celular' in data:
            lead.telefone_celular = data['telefone_celular']
        if 'segmento' in data:
            lead.segmento = data['segmento']
        if 'status_lead' in data:
            lead.status_lead = data['status_lead']
        if 'observacoes' in data:
            lead.observacoes = data['observacoes']
        
        lead.data_ultima_atualizacao = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'success': True, 'lead': lead.to_dict()})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/leads/<int:lead_id>', methods=['DELETE'])
def delete_lead(lead_id):
    try:
        lead = Lead.query.get_or_404(lead_id)
        db.session.delete(lead)
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/leads/<int:lead_id>/historico', methods=['GET'])
def get_lead_history(lead_id):
    try:
        historico = HistoricoInteracao.query.filter_by(lead_id=lead_id).order_by(HistoricoInteracao.data_interacao.desc()).all()
        return jsonify({
            'success': True,
            'historico': [h.to_dict() for h in historico]
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/leads/<int:lead_id>/historico', methods=['POST'])
def add_lead_history(lead_id):
    try:
        data = request.get_json()
        
        historico = HistoricoInteracao(
            lead_id=lead_id,
            tipo_interacao=data['tipo_interacao'],
            descricao=data['descricao']
        )
        
        db.session.add(historico)
        db.session.commit()
        
        return jsonify({'success': True, 'historico': historico.to_dict()}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    try:
        total_leads = Lead.query.count()
        
        status_stats = {}
        for status in STATUS_LEADS:
            count = Lead.query.filter_by(status_lead=status).count()
            status_stats[status] = count
        
        segment_stats = {}
        for segmento in SEGMENTOS:
            count = Lead.query.filter_by(segmento=segmento).count()
            segment_stats[segmento] = count
        
        recent_leads = Lead.query.order_by(Lead.data_cadastro.desc()).limit(10).all()
        
        return jsonify({
            'success': True,
            'total_leads': total_leads,
            'status_stats': status_stats,
            'segment_stats': segment_stats,
            'recent_leads': [lead.to_dict() for lead in recent_leads]
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/config', methods=['GET'])
def get_config():
    return jsonify({
        'success': True,
        'segmentos': SEGMENTOS,
        'status_leads': STATUS_LEADS
    })

# Inicializar banco de dados fora do contexto de requisição
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5090, debug=True)
