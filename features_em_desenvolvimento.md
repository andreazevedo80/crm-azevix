## versão 4.02: Ciclo de Vida e Integridade de Contas
# Objetivo:
- Finalizar as regras de negócio essenciais para a entidade Conta.

# Requisitos:
- Implementar a função de desativar uma Conta (soft delete).
- Implementar a lógica para tratar filiais órfãs (definir matriz_id como NULL) quando uma matriz for desativada.
- Impedir que uma conta seja definida como sua própria matriz (validação de hierarquia circular).

## versão 5.01: Módulo de Administração (Base e Gestão de Usuários)
# Objetivo:
- Criar a estrutura do painel de administração e implementar a gestão completa do ciclo de vida dos usuários.

# Requisitos:
- Criar uma área /admin acessível apenas para a role 'admin'.
- Implementar a interface para convidar, listar, editar e desativar/reativar usuários.

## versão 5.02: Módulo de Administração (Configurações do Sistema)
# Objetivo:
- Permitir que o administrador configure parâmetros essenciais do sistema.

# Requisitos:
- Implementar a interface para gerenciar os domínios de e-mail permitidos para convites.
- Implementar a interface para configurar os dados do servidor de e-mail (SMTP).

## versão 6.0: Workflow Inteligente de Vendas
# Objetivo:
- Dar ao administrador o poder de customizar o processo de vendas.

# Requisitos:
- Interface para o Admin gerenciar (CRUD) os Status de Lead e os Motivos de Perda.
- Interface para o Admin definir as regras de transição entre os status (Workflow).
- Na tela do Lead, o campo "Status" só mostrará as transições permitidas, e exigirá um "Motivo de Perda" quando aplicável.

## versão 6.01: Módulo de Propostas (Estrutura e Custos)
# Objetivo:
- Implementar o módulo de propostas, o coração financeiro do CRM.

# Requisitos da feature:
- Ser capaz de criar propostas detalhadas, com múltiplos produtos/serviços de um catálogo.
- Adicionar custos (fixos/percentuais) para calcular a margem de lucro estimada.
- A lógica de custos deve ser sensível ao tipo_conta (Pública vs. Privada).
- Propostas devem ter status e prazos.

# versão 7.01 [Automação de Documentos e Comunicação]
# Objetivo
- Automatizar a criação e o envio de propostas.

# Requisitos da feature:
- O sistema deve gerar um documento PDF profissional e personalizável a partir dos dados de uma proposta.
- Deve ser possível enviar a proposta gerada por e-mail diretamente do sistema, usando o e-mail configurado do vendedor.
- Se possível, permita customização de template do PDF por empresa (branding).

# O que será modificado:
- backend/propostas.py: Adicionar a rota para geração de PDF e a lógica de envio de e-mail.
- backend/email.py (Novo): Módulo utilitário para envio de e-mails, lendo as configurações do banco de dados.

# versão 8.01 [Módulo de Relatórios e Dashboard Inteligente]
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