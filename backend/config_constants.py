# --- Arquivo central para constantes do sistema ---

# --- ALTERAÇÃO v9.3: Define os status padrão com mais detalhes ---
STATUS_LEADS_PADRAO = [
    {'nome': 'Novo', 'estagio_alvo': 'Lead', 'is_initial_status': True},
    {'nome': 'Tentando Contato', 'estagio_alvo': 'Lead'},
    {'nome': 'Contatado', 'estagio_alvo': 'Lead'},
    {'nome': 'Interesse Demonstrado', 'estagio_alvo': 'Lead'},
    {'nome': 'Qualificado', 'estagio_alvo': 'Oportunidade'},
    {'nome': 'Reunião Agendada', 'estagio_alvo': 'Oportunidade'},
    {'nome': 'Proposta Apresentada', 'estagio_alvo': 'Oportunidade'},
    {'nome': 'Em Negociação', 'estagio_alvo': 'Oportunidade'},
    {'nome': 'Aguardando Aprovação', 'estagio_alvo': 'Oportunidade'},
    {'nome': 'Ganho', 'estagio_alvo': 'Cliente'},
    {'nome': 'Perdido', 'estagio_alvo': 'Oportunidade', 'is_loss_status': True},
    {'nome': 'Não Qualificado', 'estagio_alvo': 'Lead', 'is_loss_status': True},
]

# --- ADIÇÃO v9.3: Listas padrão para Motivos de Perda e Segmentos ---
MOTIVOS_PERDA_PADRAO = [
    'Preço', 'Concorrência', 'Timing', 'Sem Orçamento', 'Sem Fit com o Produto'
]

SEGMENTOS_PADRAO = [
    'Tecnologia', 'Saúde', 'Educação', 'Varejo', 'Serviços', 
    'Indústria', 'Agronegócio', 'Financeiro', 'Imobiliário', 'Outros'
]

# O novo Estágio do Ciclo de Vida
ESTAGIOS_CICLO_VIDA = ['Lead', 'Oportunidade', 'Cliente', 'Cliente Cancelado']

# O novo Termômetro de Vendas
TEMPERATURAS = ['Quente', 'Morno', 'Frio']