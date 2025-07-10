from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy import Index
from .utils import encrypt_data, decrypt_data # Importa as funções de criptografia

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    name = db.Column(db.String(150), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), default='vendedor', nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relações
    contas = db.relationship('Conta', backref='owner', lazy=True)
    leads = db.relationship('Lead', backref='owner', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Conta(db.Model):
    __tablename__ = 'contas'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    razao_social = db.Column(db.String(255))
    nome_fantasia = db.Column(db.String(255), nullable=False, index=True)
    _cnpj = db.Column("cnpj", db.String(255), unique=True, nullable=True) # Armazenamento criptografado
    
    tipo_conta = db.Column(db.String(50), nullable=False, default='Privada')
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    
    contatos = db.relationship('Contato', backref='conta', lazy='dynamic', cascade='all, delete-orphan')
    leads = db.relationship('Lead', backref='conta', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def cnpj(self):
        return decrypt_data(self._cnpj)

    @cnpj.setter
    def cnpj(self, value):
        self._cnpj = encrypt_data(value)

class Contato(db.Model):
    __tablename__ = 'contatos'
    id = db.Column(db.Integer, primary_key=True)
    conta_id = db.Column(db.Integer, db.ForeignKey('contas.id'), nullable=False, index=True)
    
    nome = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=True, index=True)
    telefone = db.Column(db.String(50), nullable=True)
    cargo = db.Column(db.String(100), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

# Lead agora é uma Oportunidade
class Lead(db.Model):
    __tablename__ = 'leads'
    id = db.Column(db.Integer, primary_key=True)
    
    conta_id = db.Column(db.Integer, db.ForeignKey('contas.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    contato_id = db.Column(db.Integer, db.ForeignKey('contatos.id'), nullable=True)
    
    titulo = db.Column(db.String(255), nullable=False)
    status_lead = db.Column(db.String(50), nullable=False, default='NOVO_LEAD')
    valor_estimado = db.Column(db.Numeric(10, 2), nullable=True)
    
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    data_ultima_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class HistoricoAlteracao(db.Model):
    __tablename__ = 'historico_alteracoes'
    id = db.Column(db.Integer, primary_key=True)
    data_alteracao = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Rastreia qual entidade foi alterada
    conta_id = db.Column(db.Integer, db.ForeignKey('contas.id'), nullable=True)
    contato_id = db.Column(db.Integer, db.ForeignKey('contatos.id'), nullable=True)
    lead_id = db.Column(db.Integer, db.ForeignKey('leads.id'), nullable=True)
    
    campo = db.Column(db.String(100), nullable=False)
    valor_antigo = db.Column(db.Text)
    valor_novo = db.Column(db.Text)