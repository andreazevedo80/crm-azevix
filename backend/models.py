from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy import Index
from .utils import encrypt_data, decrypt_data, format_cnpj, get_cnpj_hash

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    name = db.Column(db.String(150), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), default='vendedor', nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    contas = db.relationship('Conta', backref='owner', lazy=True, foreign_keys='Conta.user_id')
    leads = db.relationship('Lead', backref='owner', lazy=True)
    def set_password(self, password): self.password_hash = generate_password_hash(password)
    def check_password(self, password): return check_password_hash(self.password_hash, password)

class Conta(db.Model):
    __tablename__ = 'contas'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # --- RELACIONAMENTO MATRIZ/FILIAL CORRIGIDO ---
    matriz_id = db.Column(db.Integer, db.ForeignKey('contas.id'), nullable=True)
    filiais = db.relationship('Conta', backref=db.backref('matriz', remote_side=[id]), lazy='dynamic')
    
    razao_social = db.Column(db.String(255))
    nome_fantasia = db.Column(db.String(255), nullable=False, index=True)
    _cnpj_encrypted = db.Column("cnpj_encrypted", db.String(255), nullable=True)
    cnpj_hash = db.Column(db.String(64), unique=True, nullable=True, index=True)
    tipo_conta = db.Column(db.String(50), nullable=False, default='Privada')
    segmento = db.Column(db.String(100), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    contatos = db.relationship('Contato', backref='conta', lazy='dynamic', cascade='all, delete-orphan')
    leads = db.relationship('Lead', backref='conta', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def cnpj(self):
        return format_cnpj(decrypt_data(self._cnpj_encrypted))

    @cnpj.setter
    def cnpj(self, value):
        if value:
            self._cnpj_encrypted = encrypt_data(value)
            self.cnpj_hash = get_cnpj_hash(value)
        else:
            self._cnpj_encrypted = None
            self.cnpj_hash = None
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome_fantasia': self.nome_fantasia,
            'razao_social': self.razao_social,
            'cnpj': self.cnpj,
            'tipo_conta': self.tipo_conta,
            'segmento': self.segmento,
            'owner_id': self.user_id,
            'owner_name': self.owner.name if self.owner else 'N/D',
            'matriz_id': self.matriz_id,
            'matriz_nome': self.matriz.nome_fantasia if self.matriz else None,
            'filiais': [{'id': f.id, 'nome_fantasia': f.nome_fantasia} for f in self.filiais]
        }

class Contato(db.Model):
    __tablename__ = 'contatos'
    id = db.Column(db.Integer, primary_key=True)
    conta_id = db.Column(db.Integer, db.ForeignKey('contas.id'), nullable=False, index=True)
    nome = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=True, index=True)
    telefone = db.Column(db.String(50), nullable=True)
    cargo = db.Column(db.String(100), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    def to_dict(self): return {'id': self.id, 'nome': self.nome, 'email': self.email, 'telefone': self.telefone, 'cargo': self.cargo}

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
    def to_dict(self):
        contato_principal = Contato.query.get(self.contato_id) if self.contato_id else None
        return {'id': self.id, 'titulo': self.titulo, 'status_lead': self.status_lead, 'valor_estimado': str(self.valor_estimado) if self.valor_estimado else '0.00', 'data_cadastro': self.data_cadastro.strftime('%d/%m/%Y'), 'contato_principal_nome': contato_principal.nome if contato_principal else 'N/A'}

class HistoricoAlteracao(db.Model):
    __tablename__ = 'historico_alteracoes'
    id = db.Column(db.Integer, primary_key=True)
    data_alteracao = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    conta_id = db.Column(db.Integer, db.ForeignKey('contas.id'), nullable=True)
    contato_id = db.Column(db.Integer, db.ForeignKey('contatos.id'), nullable=True)
    lead_id = db.Column(db.Integer, db.ForeignKey('leads.id'), nullable=True)
    campo = db.Column(db.String(100), nullable=False)
    valor_antigo = db.Column(db.Text)
    valor_novo = db.Column(db.Text)