### Plano de Ação Mestre (Revisão 8.3 - Novos itens) 
## versão 6.1: Gestão de Leads para Gerentes e Admins
Objetivo: Dar aos gestores as ferramentas para gerenciar suas equipes.

# Requisitos:
- Adicionar contador de leads por status (métricas básicas)
- Na tela /leads, um gerente poderá filtrar para ver os leads de seus liderados.
- Implementar a funcionalidade de "Reatribuir Lead" para gerentes e admins.
🔄 Reatribuir lead: use log de auditoria para rastrear essas ações também.

## versão 7.0: Módulo de Administração (Configurações do Sistema)
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

## versão 8.0: Importação de Dados
Objetivo: Permitir que o administrador importe uma base de leads de uma planilha.

# Requisitos:
- Criar uma interface no painel de admin para upload de arquivos CSV.
- Implementar a lógica no backend para processar o arquivo e criar os leads no "Lead Pool".
- Validação de dados na importação
- Preview dos dados antes da importação
- Relatório de erros/sucessos na importação
👀 Verifique como validar CNPJs duplicados ou dados inconsistentes.
💡 Sugestão: armazene o histórico de importações (quem fez, quando, quantos registros).

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

## versão 10.0: Catálogo de Produtos e Serviços
O que é? Na v10.00, planejamos adicionar "produtos/serviços" a uma proposta. Mas de onde eles vêm?
Como funciona: Antes de criar propostas, o Admin precisaria de uma área no painel de administração para cadastrar o Catálogo de Produtos e Serviços da empresa. Cada item do catálogo teria:
Nome ("Licença do Software XPTO - Anual").
Preço unitário.
Descrição.
Talvez um "Tipo" (Produto, Serviço, Manutenção).

Por que é importante? Isso padroniza as propostas, evita erros de digitação nos preços e permite gerar relatórios futuros muito mais inteligentes (ex: "Qual foi o nosso produto mais vendido no último trimestre?").

## versão 11.0: Módulo de Propostas (Estrutura e Custos)
# Objetivo:
- Implementar o módulo de propostas, o coração financeiro do CRM.

# Requisitos da feature:
- Ser capaz de criar propostas detalhadas, com múltiplos produtos/serviços de um catálogo.
- Adicionar custos (fixos/percentuais) para calcular a margem de lucro estimada.
- A lógica de custos deve ser sensível ao tipo_conta (Pública vs. Privada).
- Propostas devem ter status e prazos.
💡 Use enum/status para controlar fluxo de propostas (Ex: RASCUNHO, ENVIADA, ACEITA, REJEITADA).

# versão 12.0 [Automação de Documentos e Comunicação]
# Objetivo
- Automatizar a criação e o envio de propostas.

# Requisitos da feature:
- O sistema deve gerar um documento PDF profissional e personalizável a partir dos dados de uma proposta.
- Deve ser possível enviar a proposta gerada por e-mail diretamente do sistema, usando o e-mail configurado do vendedor.
- Se possível, permita customização de template do PDF por empresa (branding).

# O que será modificado:
- backend/propostas.py: Adicionar a rota para geração de PDF e a lógica de envio de e-mail.
- backend/email.py (Novo): Módulo utilitário para envio de e-mails, lendo as configurações do banco de dados.

## versão 13.0 versão 12.0: Módulo de Atividades e Tarefas
O que é? Atualmente, o trabalho do vendedor está implícito no "Status da Oportunidade". Mas e as ações concretas? "Ligar para o cliente na terça-feira", "Enviar o e-mail de follow-up até as 17h", "Agendar a demonstração para a próxima semana".
Como funciona: Criaríamos uma nova entidade Atividade (ou Tarefa). Uma Atividade teria:
Um tipo (Ligação, E-mail, Reunião, Tarefa).
Uma data_prazo.
Um status (Pendente, Concluída).
Uma associação a uma Conta, Contato ou Lead.
Por que é importante? Isso transforma o CRM de um sistema de registro (o que foi feito) em um sistema de produtividade (o que precisa ser feito). O Dashboard, por exemplo, poderia ter uma seção "Minhas Tarefas para Hoje".


# versão 14.0 [Módulo de Relatórios e Dashboard Inteligente]
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