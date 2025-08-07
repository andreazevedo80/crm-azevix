from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from sqlalchemy import Index, JSON
from .utils import encrypt_data, decrypt_data, format_cnpj, get_cnpj_hash
from uuid import uuid4

# --- Modelo para configurações globais ---
class ConfigGlobal(db.Model):
    __tablename__ = 'config_global'
    key = db.Column(db.String(255), primary_key=True)
    value = db.Column(db.Text, nullable=True)
    is_encrypted = db.Column(db.Boolean, default=False)

    @classmethod
    def get_setting(cls, key, default=None):
        setting = cls.query.get(key)
        if not setting:
            return default
        if setting.is_encrypted:
            return decrypt_data(setting.value)
        return setting.value

# --- Tabela de associação para o workflow de status ---
status_transicoes = db.Table('status_transicoes',
    db.Column('status_origem_id', db.Integer, db.ForeignKey('config_status_lead.id'), primary_key=True),
    db.Column('status_destino_id', db.Integer, db.ForeignKey('config_status_lead.id'), primary_key=True)
)
# --- Novos modelos para entidades de vendas configuráveis ---
class ConfigStatusLead(db.Model):
    __tablename__ = 'config_status_lead'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    descricao = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    estagio_alvo = db.Column(db.String(50), nullable=True)
    is_loss_status = db.Column(db.Boolean, default=False, nullable=False)
    is_initial_status = db.Column(db.Boolean, default=False, nullable=False)

    # --- Relacionamento para as regras de transição ---
    proximos_status = db.relationship(
        'ConfigStatusLead', 
        secondary=status_transicoes,
        primaryjoin=(id == status_transicoes.c.status_origem_id),
        secondaryjoin=(id == status_transicoes.c.status_destino_id),
        backref=db.backref('status_anteriores', lazy='dynamic'),
        lazy='dynamic'
    )

    def to_dict(self):
        return {
            'id': self.id, 'nome': self.nome, 'descricao': self.descricao, 
            'is_active': self.is_active, 'estagio_alvo': self.estagio_alvo,
            'is_loss_status': self.is_loss_status, 'is_initial_status': self.is_initial_status,
            # --- ADIÇÃO v9.1: Inclui os IDs dos próximos status permitidos ---
            'proximos_status_ids': [status.id for status in self.proximos_status]
        }

class ConfigMotivosPerda(db.Model):
    __tablename__ = 'config_motivos_perda'
    id = db.Column(db.Integer, primary_key=True)
    motivo = db.Column(db.String(255), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    def to_dict(self):
        return {'id': self.id, 'motivo': self.motivo, 'is_active': self.is_active}

class ConfigSegmento(db.Model):
    __tablename__ = 'config_segmento'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    def to_dict(self):
        return {'id': self.id, 'nome': self.nome, 'is_active': self.is_active}

# --- Modelo para Domínios Permitidos ---
class DominiosPermitidos(db.Model):
    __tablename__ = 'dominios_permitidos'
    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(255), unique=True, nullable=False)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {'id': self.id, 'domain': self.domain}

# --- Tabela de associação para a relação Muitos-para-Muitos User <-> Role ---
user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True)
)

# --- Modelo para os Papéis (Roles) ---
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
    
    # --- Campos e relações para hierarquia e permissões ---
    gerente_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    roles = db.relationship('Role', secondary=user_roles, lazy='subquery',
                            backref=db.backref('users', lazy=True))
    liderados = db.relationship('User', backref=db.backref('gerente', remote_side=[id]), lazy='dynamic')
    
    # --- Campos para o fluxo de convite ---
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

    # --- Função auxiliar para verificar o papel do usuário ---
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
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    matriz_id = db.Column(db.Integer, db.ForeignKey('contas.id', ondelete='SET NULL'), nullable=True)
    razao_social = db.Column(db.String(255))
    nome_fantasia = db.Column(db.String(255), nullable=False, index=True)
    _cnpj_encrypted = db.Column("cnpj_encrypted", db.String(255), nullable=True)
    cnpj_hash = db.Column(db.String(64), unique=True, nullable=True, index=True)
    tipo_conta = db.Column(db.String(50), nullable=False, default='Privada')
    segmento = db.Column(db.String(100), nullable=True)
    
    # --- ADIÇÃO v9.4: Campos de Endereço ---
    cep = db.Column(db.String(20), nullable=True)
    logradouro = db.Column(db.String(255), nullable=True)
    numero = db.Column(db.String(20), nullable=True)
    bairro = db.Column(db.String(100), nullable=True)
    cidade = db.Column(db.String(100), nullable=True)
    estado = db.Column(db.String(50), nullable=True)
    
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
            # --- ADIÇÃO v9.4: Inclui os campos de endereço no dicionário ---
            'cep': self.cep,
            'logradouro': self.logradouro,
            'numero': self.numero,
            'bairro': self.bairro,
            'cidade': self.cidade,
            'estado': self.estado,
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
    
    # --- Campos para o processo de vendas ---
    estagio_ciclo_vida = db.Column(db.String(50), nullable=False, default='Lead')
    temperatura = db.Column(db.String(50), default='Morno') # Quente, Morno, Frio
    follow_up_necessario = db.Column(db.Boolean, default=False, nullable=False)
    motivo_perda = db.Column(db.String(255), nullable=True)
    
    # --- Campos de auditoria de apropriação ---
    data_apropriacao = db.Column(db.DateTime, nullable=True)
    
    # --- ADIÇÃO v11.0: Relacionamento com Propostas ---
    propostas = db.relationship('Proposta', backref='lead', lazy='dynamic')
    
    def to_dict(self):
        contato_principal = Contato.query.get(self.contato_id) if self.contato_id else None
        return {
            'id': self.id,
            'titulo': self.titulo,
            'status_lead': self.status_lead,
            'valor_estimado': str(self.valor_estimado) if self.valor_estimado else '0.00',
            'data_cadastro': self.data_cadastro.strftime('%d/%m/%Y') if self.data_cadastro else None,
            'contato_principal_nome': contato_principal.nome if contato_principal else 'N/A',
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

# --- Novo modelo para Histórico de Importações ---
class HistoricoImportacao(db.Model):
    __tablename__ = 'historico_importacoes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    nome_arquivo = db.Column(db.String(255), nullable=False)
    data_importacao = db.Column(db.DateTime, default=datetime.utcnow)
    sucesso_count = db.Column(db.Integer, default=0)
    erro_count = db.Column(db.Integer, default=0)
    erros = db.Column(JSON, nullable=True) # Armazena a lista de erros em formato JSON
    
    # Relacionamento com o usuário que importou
    importer = db.relationship('User', backref='importacoes')

    def to_dict(self):
        return {
            'id': self.id,
            'user_name': self.importer.name if self.importer else 'Desconhecido',
            'nome_arquivo': self.nome_arquivo,
            'data_importacao': self.data_importacao.strftime('%d/%m/%Y %H:%M'),
            'sucesso_count': self.sucesso_count,
            'erro_count': self.erro_count,
            'erros': self.erros or []
        }

# --- Tabelas de associação para o Catálogo Avançado ---

# Tabela para a relação Muitos-para-Muitos entre Pacotes e Itens do Catálogo
pacote_itens = db.Table('pacote_itens',
    db.Column('pacote_id', db.Integer, db.ForeignKey('pacote_servico.id'), primary_key=True),
    db.Column('produto_servico_id', db.Integer, db.ForeignKey('produto_servico.id'), primary_key=True)
)

# Tabela para a relação Muitos-para-Muitos entre Serviços e Atividades Padrão
servico_atividades = db.Table('servico_atividades',
    db.Column('servico_id', db.Integer, db.ForeignKey('produto_servico.id'), primary_key=True),
    db.Column('atividade_id', db.Integer, db.ForeignKey('atividade_padrao.id'), primary_key=True)
)

# --- ADIÇÃO v10.1: Novo modelo para Atividades Padrão ---
class AtividadePadrao(db.Model):
    __tablename__ = 'atividade_padrao'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False, unique=True)
    descricao = db.Column(db.Text)
    horas_estimadas = db.Column(db.Numeric(10, 2))
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    def to_dict(self):
        return {
            'id': self.id, 'nome': self.nome, 'descricao': self.descricao,
            'horas_estimadas': str(self.horas_estimadas) if self.horas_estimadas else '0.00',
            'is_active': self.is_active
        }

# --- Modelo para Pacotes de Serviços ---
class PacoteServico(db.Model):
    __tablename__ = 'pacote_servico'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False, unique=True)
    descricao = db.Column(db.Text)
    preco_total = db.Column(db.Numeric(10, 2))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    itens = db.relationship(
        'ProdutoServico', 
        secondary=pacote_itens,
        lazy='subquery',
        backref=db.backref('pacotes', lazy=True)
    )

    def to_dict(self):
        return {
            'id': self.id, 'nome': self.nome, 'descricao': self.descricao,
            'preco_total': str(self.preco_total) if self.preco_total else '0.00',
            'is_active': self.is_active,
            'item_ids': [item.id for item in self.itens]
        }

# --- Modelo para o Catálogo de Produtos e Serviços ---
class ProdutoServico(db.Model):
    __tablename__ = 'produto_servico'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False, index=True)
    descricao = db.Column(db.Text)
    
    # Campos para flexibilidade de tipo e cobrança
    tipo_item = db.Column(db.String(50), nullable=False, default='Serviço Pontual') # Ex: Produto, Serviço Recorrente, Serviço Pontual, Consultoria
    tipo_cobranca = db.Column(db.String(50), nullable=False, default='Pacote') # Ex: Unitário, Mensal, Hora, Pacote
    preco_base = db.Column(db.Numeric(10, 2), nullable=True)
    preco_sob_consulta = db.Column(db.Boolean, default=False, nullable=False)
    
    # Campos específicos para licitações
    catmat_catser = db.Column(db.String(100), nullable=True)
    palavras_chave_licitacao = db.Column(db.Text, nullable=True)
    
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)

    # --- Relacionamento com Atividades Padrão ---
    atividades = db.relationship(
        'AtividadePadrao',
        secondary=servico_atividades,
        lazy='subquery',
        backref=db.backref('servicos', lazy=True)
    )

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'tipo_item': self.tipo_item,
            'tipo_cobranca': self.tipo_cobranca,
            'preco_base': str(self.preco_base) if self.preco_base is not None else '0.00',
            'preco_sob_consulta': self.preco_sob_consulta,
            'catmat_catser': self.catmat_catser,
            'palavras_chave_licitacao': self.palavras_chave_licitacao,
            'is_active': self.is_active,
            'atividade_ids': [a.id for a in self.atividades]
        }
        
# --- ADIÇÃO v11.0: Novos modelos para o Módulo de Propostas ---

class Proposta(db.Model):
    __tablename__ = 'propostas'
    id = db.Column(db.Integer, primary_key=True)
    lead_id = db.Column(db.Integer, db.ForeignKey('leads.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    contato_id = db.Column(db.Integer, db.ForeignKey('contatos.id'), nullable=True)
    
    numero_proposta = db.Column(db.String(50), unique=True, nullable=False)
    versao = db.Column(db.Integer, default=1, nullable=False)
    status = db.Column(db.String(50), default='Em elaboração', nullable=False)
    
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_envio = db.Column(db.DateTime, nullable=True)
    data_validade = db.Column(db.DateTime, nullable=True)
    
    valor_total = db.Column(db.Numeric(12, 2), default=0.00)
    
    criador = db.relationship('User', backref='propostas_criadas')
    contato_principal = db.relationship('Contato', backref='propostas')
    itens = db.relationship('ItemProposta', backref='proposta', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'lead_id': self.lead_id,
            'numero_proposta': self.numero_proposta,
            'status': self.status,
            'valor_total': str(self.valor_total) if self.valor_total is not None else '0.00',
            'data_criacao': self.data_criacao.strftime('%d/%m/%Y %H:%M')
        }

class ItemProposta(db.Model):
    __tablename__ = 'item_proposta'
    id = db.Column(db.Integer, primary_key=True)
    proposta_id = db.Column(db.Integer, db.ForeignKey('propostas.id'), nullable=False, index=True)
    produto_servico_id = db.Column(db.Integer, db.ForeignKey('produto_servico.id'), nullable=True)
    
    descricao = db.Column(db.Text, nullable=False)
    quantidade = db.Column(db.Numeric(10, 2), default=1.00)
    valor_unitario = db.Column(db.Numeric(10, 2), default=0.00)
    valor_total = db.Column(db.Numeric(12, 2), default=0.00)
    
    produto_servico = db.relationship('ProdutoServico')

    def to_dict(self):
        return {
            'id': self.id,
            'descricao': self.descricao,
            'quantidade': str(self.quantidade),
            'valor_unitario': str(self.valor_unitario),
            'valor_total': str(self.valor_total)
        }