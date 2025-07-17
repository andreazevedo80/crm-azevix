## versão 5.03: Refinamento do Processo de Vendas (A Base)
Objetivo: Enriquecer o modelo Lead com os novos campos de "Estágio de Ciclo de Vida" e "Motivo de Perda", e atualizar a interface existente para refletir essa nova inteligência.

# Requisitos:
- Adicionar as colunas estagio_ciclo_vida, motivo_perda e temperatura ao modelo Lead.
- Atualizar as STATUS_LEADS para a nova lista mais detalhada.
- Na página detalhe_conta.html, a seção de "Oportunidades/Leads" será modificada para exibir e permitir a edição de todos os novos campos, incluindo os ícones do termômetro.
- A lógica no detalhe_conta.js será aprimorada para lidar com a nova interface.

# Impacto: Esta versão prepara o terreno. Ao final dela, teremos um backend robusto, mas a gestão dos leads ainda será feita dentro de cada conta.

## versão 5.04: Módulo de Administração (Configurações do Sistema)
# Objetivo:
- Permitir que o administrador configure parâmetros essenciais do sistema.

# Requisitos:
- Implementar a interface para gerenciar os domínios de e-mail permitidos para convites.
- Implementar a interface para configurar os dados do servidor de e-mail (SMTP).
- Implementar um campo no painel de administração para que o admin possa configurar a "URL Base do Site" (SITE_URL)
- Habilitar o botão já existente em /admin/users +Convidar Novo Usuário.

## versão 6.0: Módulo de Gestão de Leads
Objetivo: Criar a nova tela principal de gestão de leads.
Requisitos:
- Criar um novo link "Leads" na barra de navegação principal.
- Este link levará a uma nova página (/leads).
- Esta página terá uma lista paginada e com busca de todos os leads aos quais o usuário tem acesso.
- A página terá filtros poderosos para que o usuário possa segmentar a lista por Estágio de Ciclo de Vida e por Status da Oportunidade.
- Ao clicar em um lead na lista, o usuário será levado para a página de detalhe_conta correspondente.

## versão 7.0: Workflow Inteligente de Vendas
# Objetivo:
- Dar ao administrador o poder de customizar o processo de vendas.

# Requisitos:
- Interface para o Admin gerenciar (CRUD) os Status de Lead e os Motivos de Perda.
- Interface para o Admin definir as regras de transição entre os status (Workflow).
- Na tela do Lead, o campo "Status" só mostrará as transições permitidas, e exigirá um "Motivo de Perda" quando aplicável.

## versão 8.01: Módulo de Propostas (Estrutura e Custos)
# Objetivo:
- Implementar o módulo de propostas, o coração financeiro do CRM.

# Requisitos da feature:
- Ser capaz de criar propostas detalhadas, com múltiplos produtos/serviços de um catálogo.
- Adicionar custos (fixos/percentuais) para calcular a margem de lucro estimada.
- A lógica de custos deve ser sensível ao tipo_conta (Pública vs. Privada).
- Propostas devem ter status e prazos.

# versão 9.01 [Automação de Documentos e Comunicação]
# Objetivo
- Automatizar a criação e o envio de propostas.

# Requisitos da feature:
- O sistema deve gerar um documento PDF profissional e personalizável a partir dos dados de uma proposta.
- Deve ser possível enviar a proposta gerada por e-mail diretamente do sistema, usando o e-mail configurado do vendedor.
- Se possível, permita customização de template do PDF por empresa (branding).

# O que será modificado:
- backend/propostas.py: Adicionar a rota para geração de PDF e a lógica de envio de e-mail.
- backend/email.py (Novo): Módulo utilitário para envio de e-mails, lendo as configurações do banco de dados.

# versão 10.01 [Módulo de Relatórios e Dashboard Inteligente]
# Objetivo
- Fornecer inteligência de negócio, consolidando os dados em relatórios e em um dashboard dinâmico.

# Requisitos da feature:
- O Dashboard deve exibir um Funil de Vendas visual (quantos R$ estão em cada etapa do funil).
- O Dashboard deve mostrar métricas chave: Taxa de Conversão, Valor Médio das Propostas, etc.
- Deve haver uma página de Relatórios com filtros (por data, por vendedor) para analisar o desempenho de vendas.
- Todos os relatórios devem ser exportáveis para PDF.
 - Considere incluir exportação para Excel/CSV em versões futuras, além de permitir agendamento de envio periódico.

# O que será modificado:
- backend/relatorios.py (Novo): Blueprint para gerar os dados para os relatórios.
- backend/main.py: Rota do dashboard será modificada para consumir os dados da API de relatórios.
- backend/templates/dashboard.html: Substituição do conteúdo estático por gráficos dinâmicos.