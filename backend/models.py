from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), default='vendedor')
    leads = db.relationship('Lead', backref='owner', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Lead(db.Model):
    __tablename__ = 'leads'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    nome_completo = db.Column(db.String(200), nullable=False)
    nome_conta = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=True)
    telefone_fixo = db.Column(db.String(20))
    telefone_celular = db.Column(db.String(20))
    segmento = db.Column(db.String(50), nullable=False)
    status_lead = db.Column(db.String(50), nullable=False, default='NOVO_LEAD')
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    data_ultima_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    observacoes = db.Column(db.Text)
    historico_interacoes = db.relationship('HistoricoInteracao', backref='lead', lazy=True, cascade='all, delete-orphan')

    # MODIFICADO: Agora retorna TODOS os campos necessários para o frontend
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
            'observacoes': self.observacoes,
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None,
            'owner_name': self.owner.name if self.owner else 'N/D'
        }

class HistoricoInteracao(db.Model):
    __tablename__ = 'historico_interacoes'
    id = db.Column(db.Integer, primary_key=True)
    lead_id = db.Column(db.Integer, db.ForeignKey('leads.id'), nullable=False)
    tipo_interacao = db.Column(db.String(50), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    data_interacao = db.Column(db.DateTime, default=datetime.utcnow)