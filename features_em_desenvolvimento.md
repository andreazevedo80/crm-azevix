### Plano de Ação Mestre (Revisão 8.2 - Proposta Reorganizada)

# versão 6.0: Módulo de Gestão de Leads (A Nova Tela)
Objetivo: Criar a nova interface central para a gestão do funil de vendas.

# Requisitos:
- Criar um novo link e página /leads, na barra de navegação principal.
- Este link levará a uma nova página (/leads).
- A página exibirá o "Lead Pool" (leads sem dono) e os leads do próprio usuário.
- Implementar o botão e a lógica de "Assumir Lead".
- Implementar uma verificação no momento de salvar "Assumir Lead", para garantir que o lead ainda não tem um dono.
- Criar filtros poderosos por Estágio, Status e o novo flag de "Follow-up".
- Implementar paginação desde o início
- Adicionar contador de leads por status (métricas básicas)
- Incluir busca por nome/empresa
- Adicionar botão na pagina detalhe_conta.htlm "Adicionar Nova Oportunidade"
- Ao clicar em um lead na lista, o usuário será levado para a página de detalhe_conta correspondente.
📊 Filtros: se forem muitos, pense em URL parametrizada para facilitar bookmarks e análises.

## versão 6.1: Gestão de Leads para Gerentes e Admins
Objetivo: Dar aos gestores as ferramentas para gerenciar suas equipes.

# Requisitos:
- Na tela /leads, um gerente poderá filtrar para ver os leads de seus liderados.
- Implementar a funcionalidade de "Reatribuir Lead" para gerentes e admins.
🔄 Reatribuir lead: use log de auditoria para rastrear essas ações também.

## versão 7.0: Importação de Dados
Objetivo: Permitir que o administrador importe uma base de leads de uma planilha.

# Requisitos:
- Criar uma interface no painel de admin para upload de arquivos CSV.
- Implementar a lógica no backend para processar o arquivo e criar os leads no "Lead Pool".
- Validação de dados na importação
- Preview dos dados antes da importação
- Relatório de erros/sucessos na importação
👀 Verifique como validar CNPJs duplicados ou dados inconsistentes.
💡 Sugestão: armazene o histórico de importações (quem fez, quando, quantos registros).

## versão 8.0: Módulo de Administração (Configurações do Sistema)
# Objetivo:
- Permitir que o administrador configure parâmetros essenciais do sistema.

# Requisitos:
- Implementar a interface para gerenciar os domínios de e-mail permitidos para convites.
- Implementar a interface para configurar os dados do servidor de e-mail (SMTP).
- Implementar um campo no painel de administração para que o admin possa configurar a "URL Base do Site" (SITE_URL)
- Habilitar o botão já existente em /admin/users +Convidar Novo Usuário.
📨 Configuração de SMTP é sensível — prever testes antes de salvar.
- Configurações da Empresa, Nome da empresa, endereço... contato... etc (ara usar futuramente nas propostas e relatórios).
👮 Cuidado com convites indevidos e com o reset de tokens vencidos.

## versão 9.0: Workflow Inteligente de Vendas
# Objetivo:
- Dar ao administrador o poder de customizar o processo de vendas.

# Requisitos:
- Implementar validações de negócio para transições de status
- Interface para o Admin gerenciar (CRUD) os Status de Lead e os Motivos de Perda.
- Interface para o Admin definir as regras de transição entre os status (Workflow).
- Na tela do Lead, o campo "Status" só mostrará as transições permitidas, e exigirá um "Motivo de Perda" quando aplicável.
⚠️ Atenção à integridade dos dados: se um admin remove um status, o que acontece com os leads existentes?
🔍 Validações de transição de status: sugiro uma tabela auxiliar status_transicoes com regras, para evitar lógica engessada no código.

## versão 10.00: Módulo de Propostas (Estrutura e Custos)
# Objetivo:
- Implementar o módulo de propostas, o coração financeiro do CRM.

# Requisitos da feature:
- Ser capaz de criar propostas detalhadas, com múltiplos produtos/serviços de um catálogo.
- Adicionar custos (fixos/percentuais) para calcular a margem de lucro estimada.
- A lógica de custos deve ser sensível ao tipo_conta (Pública vs. Privada).
- Propostas devem ter status e prazos.
💡 Use enum/status para controlar fluxo de propostas (Ex: RASCUNHO, ENVIADA, ACEITA, REJEITADA).

# versão 11.00 [Automação de Documentos e Comunicação]
# Objetivo
- Automatizar a criação e o envio de propostas.

# Requisitos da feature:
- O sistema deve gerar um documento PDF profissional e personalizável a partir dos dados de uma proposta.
- Deve ser possível enviar a proposta gerada por e-mail diretamente do sistema, usando o e-mail configurado do vendedor.
- Se possível, permita customização de template do PDF por empresa (branding).

# O que será modificado:
- backend/propostas.py: Adicionar a rota para geração de PDF e a lógica de envio de e-mail.
- backend/email.py (Novo): Módulo utilitário para envio de e-mails, lendo as configurações do banco de dados.

# versão 11.01 [Módulo de Relatórios e Dashboard Inteligente]
# Objetivo
- Fornecer inteligência de negócio, consolidando os dados em relatórios e em um dashboard dinâmico.

# Requisitos da feature:
- O Dashboard deve exibir um Funil de Vendas visual (quantos R$ estão em cada etapa do funil).
- O Dashboard deve mostrar métricas chave: Taxa de Conversão, Valor Médio das Propostas, etc.
- Deve haver uma página de Relatórios com filtros (por data, por vendedor) para analisar o desempenho de vendas.
- Todos os relatórios devem ser exportáveis para PDF.
 - Considere incluir exportação para Excel/CSV em versões futuras, além de permitir agendamento de envio periódico.
⚙️ Armazenar logs de envio seria útil (data, destinatário, sucesso/erro).
📨 E-mail por usuário exige validação de credenciais (OAuth ou SMTP direto?)