from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from sqlalchemy import Index
from .utils import encrypt_data, decrypt_data, format_cnpj, get_cnpj_hash
from uuid import uuid4

# --- ADIÇÃO: Tabela de associação para a relação Muitos-para-Muitos User <-> Role ---
user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True)
)

# --- ADIÇÃO: Novo modelo para os Papéis (Roles) ---
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    name = db.Column(db.String(150), nullable=False)
    password_hash = db.Column(db.String(256), nullable=True)
    is_active = db.Column(db.Boolean, default=False, nullable=False)

    # --- REMOVIDO: O campo de texto 'role' foi removido ---
    # role = db.Column(db.String(50), default='vendedor', nullable=False)
    
    # --- ADIÇÃO: Novos campos e relações para hierarquia e permissões ---
    gerente_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    roles = db.relationship('Role', secondary=user_roles, lazy='subquery',
                            backref=db.backref('users', lazy=True))
    liderados = db.relationship('User', backref=db.backref('gerente', remote_side=[id]), lazy='dynamic')
    
    # --- ADIÇÃO: Novos campos para o fluxo de convite ---
    invitation_token = db.Column(db.String(255), unique=True, nullable=True)
    invitation_expiration = db.Column(db.DateTime, nullable=True)
    
    
    # Relações existentes preservadas
    contas = db.relationship('Conta', backref='owner', lazy=True, foreign_keys='Conta.user_id')
    leads = db.relationship('Lead', backref='owner', lazy=True)
    
    def set_password(self, password): self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        # Garante que o password_hash não é nulo antes de verificar
        if self.password_hash is None:
            return False
        return check_password_hash(self.password_hash, password)

    # --- ADIÇÃO: Função auxiliar para verificar o papel do usuário ---
    def has_role(self, role_name):
        """Verifica se o usuário possui um determinado papel."""
        for role in self.roles:
            if role.name == role_name:
                return True
        return False

    def generate_invitation_token(self):
        self.invitation_token = str(uuid4())
        self.invitation_expiration = datetime.utcnow() + timedelta(hours=24)

class Conta(db.Model):
    __tablename__ = 'contas'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    matriz_id = db.Column(db.Integer, db.ForeignKey('contas.id', ondelete='SET NULL'), nullable=True)
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
    filiais = db.relationship('Conta', backref=db.backref('matriz', remote_side=[id]), lazy=True)

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
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    contato_id = db.Column(db.Integer, db.ForeignKey('contatos.id'), nullable=True)
    titulo = db.Column(db.String(255), nullable=False)
    status_lead = db.Column(db.String(50), nullable=False, default='Novo')
    valor_estimado = db.Column(db.Numeric(10, 2), nullable=True)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    data_ultima_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # --- ADIÇÃO v5.03: Novos campos para o processo de vendas ---
    estagio_ciclo_vida = db.Column(db.String(50), nullable=False, default='Lead')
    temperatura = db.Column(db.String(50), default='Morno') # Quente, Morno, Frio
    follow_up_necessario = db.Column(db.Boolean, default=False, nullable=False)
    motivo_perda = db.Column(db.String(255), nullable=True)
    
    # --- ADIÇÃO v5.03: Campos de auditoria de apropriação ---
    data_apropriacao = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        contato_principal = Contato.query.get(self.contato_id) if self.contato_id else None
        return {
            'id': self.id,
            'titulo': self.titulo,
            'status_lead': self.status_lead,
            'valor_estimado': str(self.valor_estimado) if self.valor_estimado else '0.00',
            'data_cadastro': self.data_cadastro.strftime('%d/%m/%Y'),
            'contato_principal_nome': contato_principal.nome if contato_principal else 'N/A',
            # --- ADIÇÃO v5.03: Incluindo novos campos na resposta da API ---
            'estagio_ciclo_vida': self.estagio_ciclo_vida,
            'temperatura': self.temperatura,
            'follow_up_necessario': self.follow_up_necessario,
            'motivo_perda': self.motivo_perda
        }

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