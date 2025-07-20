## 📅 Roadmap de Desenvolvimento

### ✅ Versões Concluídas
- **1.0** – Autenticação e estrutura base
- **2.0 a 2.2** – CRUD de Leads, associação com vendedor, tipo de conta
## versão 2.03 [A Grande Reestruturação: Contas, Contatos e Integridade de Dados]
Objetivo: Criar a base de dados profissional com as entidades "Conta" e "Contato", garantindo a integridade dos dados desde o início com validações e padronizações.

# Requisitos da feature:
- A entidade Conta deve ter Razão Social, Nome Fantasia, CNPJ (criptografado), Tipo e um campo is_active para "soft delete".
- O CNPJ deve ser validado (formato e lógica de cálculo) e será o identificador único para evitar Contas duplicadas.
- A entidade Contato deve ser associada a uma Conta e conter nome, email, telefone, cargo e um campo is_active.
- Os números de telefone devem ser padronizados e normalizados no backend antes de serem salvos (ex: usando a biblioteca phonenumbers).
- O fluxo de criação de um novo Lead (Oportunidade) deve estar atrelado à criação/seleção de uma Conta e um Contato.
- A busca por duplicatas no fluxo de criação deve ser inteligente, normalizando os nomes para a comparação (ex: "Empresa ABC Ltda" deve ser encontrada ao buscar por "empresa abc").

# O que será modificado:
- backend/models.py: Criar os modelos Conta e Contato com os novos campos. Refatorar Lead para se conectar a Conta.
- backend/contas.py (Novo): Criar o Blueprint e as APIs para gerenciar o CRUD de Contas e Contatos, incluindo a lógica de validação, normalização e criptografia.
- backend/templates/: Criar as novas telas de cadastro que refletem o novo fluxo.

### versão 2.04 [Visualização e Gestão de Contas e Contatos]
Objetivo: Criar a página de "Detalhes da Conta", que será o hub central para todas as interações com um cliente, e permitir a gestão de múltiplos contatos.

# Requisitos da feature:
- Na lista de contas, o botão "Detalhes" (atualmente desativado) deverá funcionar, levando para uma nova página (/contas/<id>).
- A página de detalhes deve exibir todas as informações da Conta.
- A página deve ter uma seção para listar todos os Contatos associados àquela Conta.
- Nesta mesma seção, deve haver um formulário ou botão para adicionar novos Contatos a uma Conta já existente.
- A página também deve ter uma seção para listar todas as Oportunidades (Leads) associadas àquela Conta.

# O que será modificado:
- backend/contas.py: Criar a nova rota /contas/<id> e a API para buscar os detalhes completos de uma conta, incluindo seus contatos e leads.
- backend/templates/contas/detalhe_conta.html (Novo): Criar a nova tela de visualização.
- backend/static/js/detalhe_conta.js (Novo): Criar o JavaScript para gerenciar a interatividade da página de detalhes (como adicionar um novo contato via API sem recarregar a página).

# Requisitos da feature:
- Deve ser possível definir uma Conta como "filial" de outra Conta ("matriz").
- Na página de "Detalhes da Conta", um administrador deve ver um campo para selecionar a "Conta Matriz".
- Na mesma página, um administrador deve ver um campo para alterar o "Responsável" (o vendedor) por aquela conta.
- Na página de "Detalhes da conta", o vendedor ou administrador pode editar todos os campos da conta, contato e leads.
- No botão de ação do Leads o vendedor pode editar o Status do Lead, preço e Título da Oportunidade.

# O que será modificado:
- backend/models.py: Adicionar a coluna matriz_id na tabela Conta, que se auto-referencia.
- backend/contas.py: Atualizar a API de edição de contas para permitir a alteração do user_id (dono) e do matriz_id.
- backend/templates/contas/detalhe_conta.html: Adicionar os campos de edição para o admin.

### versão 2.05: Hierarquia de Contas e Gestão de Vendedores

### versão 2.06 [Segurança e Hierarquia de Usuários]
Objetivo: Implementar um sistema de permissões robusto com diferentes papéis (Roles) e uma estrutura de gestão de equipes.

# Requisitos da feature:
- O sistema deve ter uma tabela Role no banco para armazenar os papéis ('admin', 'gerente', 'vendedor').
- O modelo User será modificado: o campo de texto role será substituído por um relacionamento com a tabela Role, e um campo gerente_id (auto-relacionamento) será adicionado para definir a hierarquia de equipes.
- O modelo User terá um campo is_active para permitir a desativação (soft delete) em vez da exclusão.

# O que será modificado:
- backend/models.py: Criar a nova tabela Role e refatorar o modelo User para incluir a relação com Role, o campo gerente_id e o campo is_active.

## versão 2.07 [Finalização da Gestão de Contas]
# Objetivo
- Concluir o ciclo de vida completo da entidade Conta, permitindo a desativação de contatos e a gestão segura da hierarquia.

# Requisitos da feature:
- Um admin/gerente/vendedor poderá "excluir" (desativar)  e "editar" um contato da página de detalhes da conta.
- Um admin/gerente poderá "excluir" (desativar) um contato da página de detalhes da conta.
- A busca por "Conta Matriz" (tanto no cadastro quanto na edição) deve impedir que uma conta seja definida como sua própria matriz.

# O que será modificado:
- backend/models.py: Adicionar a regra ondelete='SET NULL' no relacionamento matriz_id.
- backend/contas.py: Adicionar a rota DELETE /api/contatos/<int:id> e a lógica para desativação de contas e tratamento de filiais.
- backend/static/js/detalhe_conta.js: Adicionar a lógica para o botão de exclusão de contato e o filtro na busca por matriz.

# versão 3.0: Estrutura de Permissões e Hierarquia
# Objetivo:
- Modificar o banco de dados para suportar o novo sistema de permissões e gestão de equipes. Esta é a fundação de tudo.

# Requisitos:
- Criar a nova tabela Role para armazenar os papéis ('admin', 'gerente', 'vendedor').
- Refatorar o modelo User para:
- Substituir o campo de texto role por um relacionamento com a tabela Role.
- Adicionar o campo gerente_id para definir a hierarquia de equipes.
- Implementar o "seeding" automático para que os papéis essenciais sejam criados na inicialização do sistema.

# O que será modificado:
- backend/models.py: Criar a tabela Role e refatorar User.
- backend/__init__.py: Adicionar a lógica de "seeding".

## versão 3.1: Fluxo de Cadastro Seguro e Perfil do Usuário
- Objetivo:
Implementar o ciclo de vida inicial do usuário: o "onboarding" seguro através de convites e a autogestão de senha.

#Requisitos:
- Implementar a lógica de "primeiro usuário é admin" e desativar o registro público após isso.
- Criar o fluxo de convite por e-mail com link seguro e de uso único (token + tempo de expiração).
- Criar a página /perfil onde qualquer usuário logado pode alterar sua própria senha. (Este é o ponto que você sentiu falta, e ele se encaixa perfeitamente aqui).

# O que será modificado:
- backend/auth.py: Implementar toda a nova lógica de convite e ativação de conta.
- backend/user.py (Novo): Criar o Blueprint para a página de perfil.
- backend/templates/: Criar as novas telas set_password.html e perfil.html.
- backend/email.py (Novo): Módulo para o envio de e-mails.


## versão 3.2: Lógica de Negócio, Permissões e Ciclo de Vida
#Objetivo:
- Fazer a aplicação "entender" as novas regras de permissão e implementar o ciclo de vida completo para Contas e Usuários.

# Requisitos:
- Visão por Papel: A API de listagem de Contas deve respeitar a hierarquia: Admin vê tudo, Gerente vê sua equipe, Vendedor vê apenas o seu.
- Ciclo de Vida de Usuários: No futuro painel de admin, será possível desativar um usuário (soft delete, is_active = False).
- Ciclo de Vida de Contas:
- Implementar a função de desativar uma Conta.
- Implementar a lógica de tratar filiais órfãs: ao desativar uma conta matriz, suas filiais terão o matriz_id definido como NULL.

# O que será modificado:
- backend/contas.py: Ajustar a query da rota get_contas para respeitar a hierarquia gerente_id. Implementar a rota para desativar contas.
- backend/models.py: Adicionar a regra ondelete='SET NULL' ao campo matriz_id como uma camada extra de proteção no banco de dados.

### Plano de Ação e Requisitos de Software - CRM Azevix (Revisão 5.0)

## versão 4.01 [Log de Auditoria e Paginação]
# Objetivo
- Rastrear alterações importantes e garantir a performance do sistema.

# Requisitos da feature:
- O sistema deve registrar um histórico de alterações para entidades críticas como Lead e Proposta.
- Todas as listas principais devem ser paginadas para manter a aplicação rápida.

# O que será modificado:
- backend/models.py: Criar a tabela HistoricoAlteracao.
- backend/contas.py, backend/propostas.py: Adicionar a lógica para registrar o histórico nas rotas de atualização.
- backend/static/js/ e backend/*_api.py: Implementar a lógica de paginação no frontend e backend.

## versão 4.02: Ciclo de Vida e Integridade de Contas
# Objetivo:
- Finalizar as regras de negócio essenciais para a entidade Conta.

# Requisitos:
- Implementar a função de desativar uma Conta (soft delete).
- Implementar a lógica para tratar filiais órfãs (definir matriz_id como NULL) quando uma matriz for desativada.
- Impedir que uma conta seja definida como sua própria matriz (validação de hierarquia circular).

## versão 5.03: Refinamento do Processo de Vendas (A Base)
Objetivo: Enriquecer o modelo Lead com os novos campos e status para suportar o novo fluxo de vendas.

# Requisitos:
- Adicionar as colunas estagio_ciclo_vida, motivo_perda e temperatura ao modelo Lead.
- Adicionar a coluna booleana follow_up_necessario.
- Adicionar os campos de auditoria (data_apropriacao, etc.).
- Atualizar a lista STATUS_LEADS no contas.py para os novos valores.
- Implementar a lógica de mudança automática do estagio_ciclo_vida no backend.
- Adicionar logs de auditoria para mudanças de status

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



# Plano de Ação Mestre CRM - Versão 8.4
## Requisitos Organizados por Versão

---

## Versão 6.1: Gestão de Leads para Gerentes e Admins

### Requisitos Funcionais
- Adicionar contador de leads por status (métricas básicas)
- Na tela /leads, um gerente poderá filtrar para ver os leads de seus liderados
- Implementar a funcionalidade de "Reatribuir Lead" para gerentes e admins
- **[NOVO]** Implementar sistema de notificações para o vendedor quando um lead for reatribuído

### Requisitos Técnicos
- Usar log de auditoria para rastrear ações de reatribuição
- Criar tabela de notificações ou usar sistema de eventos

---

## Versão 7.0: Módulo de Administração (Configurações do Sistema)

### Requisitos Funcionais
- Implementar interface para gerenciar domínios de e-mail permitidos para convites
- Implementar interface para configurar dados do servidor de e-mail (SMTP)
- Implementar campo para configurar "URL Base do Site" (SITE_URL)
- Habilitar botão "Convidar Novo Usuário" em /admin/users
- **[NOVO]** Implementar configurações da Empresa (nome, endereço, contato, etc.)
- **[NOVO]** Implementar diferentes níveis de permissão (Super Admin vs Admin)

### Requisitos Técnicos
- Criar tabela config_global com estrutura chave-valor flexível
- **[NOVO]** Implementar criptografia para credenciais SMTP sensíveis no banco
- Implementar testes de SMTP antes de salvar configurações
- Implementar controle de tokens vencidos e prevenção de convites indevidos
- Criar sistema de hierarquia de permissões

---

## Versão 8.0: Importação de Dados

### Requisitos Funcionais
- Criar interface no painel admin para upload de arquivos CSV
- Implementar preview dos dados antes da importação
- Gerar relatório de erros/sucessos na importação
- **[NOVO]** Criar e disponibilizar templates de CSV para facilitar preparação dos dados
- **[NOVO]** Implementar histórico de importações (quem fez, quando, quantos registros)

### Requisitos Técnicos
- Implementar lógica para processar arquivo e criar leads no "Lead Pool"
- **[NOVO]** Implementar validação de encoding do CSV (UTF-8, ISO-8859-1)
- **[NOVO]** Implementar processamento assíncrono para grandes volumes
- Validar CNPJs duplicados e dados inconsistentes
- **[NOVO]** Armazenar arquivo original associado ao job de histórico
- Implementar sistema de jobs para rastreabilidade

### Requisitos de Segurança
- **[NOVO]** Implementar backup automático antes de importações grandes
- Validação robusta de dados de entrada

---

## Versão 9.0: Workflow Inteligente de Vendas

### Requisitos Funcionais
- Interface para Admin gerenciar (CRUD) Status de Lead e Motivos de Perda
- Interface para Admin definir regras de transição entre status (Workflow)
- Na tela do Lead, campo "Status" mostrará apenas transições permitidas
- Exigir "Motivo de Perda" quando aplicável
- **[NOVO]** Implementar versionamento do workflow para auditoria de mudanças
- **[NOVO]** Implementar migração automática para status "genérico" quando status é removido

### Requisitos Técnicos
- Implementar validações de negócio para transições de status
- Criar tabela `status` (lista de status disponíveis)
- Criar tabela `status_transicoes` (regras de transição)
- **[NOVO]** Criar tabela `workflow_versoes` para controle de versionamento
- Implementar lógica para lidar com leads órfãos

---

## Versão 10.0: Catálogo de Produtos e Serviços

### Requisitos Funcionais
- Área no painel admin para cadastrar Catálogo de Produtos e Serviços
- Campos: Nome, Preço unitário, Descrição, Tipo (Produto, Serviço, Manutenção)
- **[NOVO]** Implementar categorização de produtos/serviços
- **[NOVO]** Implementar sistema de descontos por volume ou cliente
- **[NOVO]** Implementar produtos combo/bundle

### Requisitos Técnicos
- Criar estrutura de banco para catálogo
- **[NOVO]** Criar tabela de categorias
- **[NOVO]** Criar tabela de regras de desconto
- **[NOVO]** Criar tabela de combos/bundles
- Permitir relatórios inteligentes por produto

---

## Versão 11.0: Módulo de Propostas (Estrutura e Custos)

### Requisitos Funcionais
- Criar propostas detalhadas com múltiplos produtos/serviços do catálogo
- Adicionar custos (fixos/percentuais) para calcular margem de lucro estimada
- Lógica de custos sensível ao tipo_conta (Pública vs. Privada)
- Propostas com status e prazos
- **[NOVO]** Implementar controle de versionamento das propostas (v1.0, v1.1, etc.)
- **[NOVO]** Implementar funcionalidade de cancelamento de proposta
- **[NOVO]** Implementar funcionalidade de duplicação de proposta

### Requisitos Técnicos
- Usar enum/status para controlar fluxo (RASCUNHO, ENVIADA, ACEITA, REJEITADA)
- **[NOVO]** Criar tabela de versões de propostas
- Implementar cálculos automáticos de margem

---

## Versão 12.0: Automação de Documentos e Comunicação

### Requisitos Funcionais
- Gerar documento PDF profissional e personalizável a partir dos dados da proposta
- Enviar proposta por e-mail diretamente do sistema usando e-mail do vendedor
- Permitir customização de template PDF por empresa (branding)
- **[NOVO]** Implementar assinatura digital das propostas
- **[NOVO]** Implementar tracking de abertura de email (pixel invisível)

### Requisitos Técnicos
- Adicionar rota para geração de PDF em backend/propostas.py
- Criar módulo backend/email.py para envio de e-mails
- Criar sistema de templates com placeholders ({{empresa.nome}}, {{proposta.valor_total}})
- **[NOVO]** Implementar sistema de assinatura digital
- **[NOVO]** Implementar sistema de tracking de emails

---

## Versão 13.0: Módulo de Atividades e Tarefas

### Requisitos Funcionais
- Criar entidade Atividade/Tarefa com campos:
  - Tipo (Ligação, E-mail, Reunião, Tarefa)
  - Data_prazo
  - Status (Pendente, Concluída)
  - Prioridade
  - Associação a Conta, Contato ou Lead
- Seção "Minhas Tarefas para Hoje" no Dashboard
- **[NOVO]** Sistema de lembretes por e-mail
- **[NOVO]** Integração com calendário

### Requisitos Técnicos
- Criar tabela de atividades
- Implementar sistema de notificações/lembretes
- **[NOVO]** Implementar integração com APIs de calendário (Google, Outlook)
- Tríade: Prioridade + Prazo + Status

---

## Versão 14.0: Módulo de Relatórios e Dashboard Inteligente

### Requisitos Funcionais
- Dashboard com Funil de Vendas visual (valores por etapa)
- Métricas chave: Taxa de Conversão, Valor Médio das Propostas
- Página de Relatórios com filtros (data, vendedor)
- Exportação de relatórios para PDF
- **[NOVO]** Exportação para Excel/CSV
- **[NOVO]** Agendamento de envio periódico de relatórios

### Requisitos Técnicos
- **[NOVO]** Usar agregações em SQL com cache Redis para performance
- **[NOVO]** Armazenar logs de envio (data, destinatário, sucesso/erro)
- **[NOVO]** Implementar validação de credenciais de e-mail (OAuth ou SMTP direto)
- Otimizar queries para relatórios

---

## Requisitos Gerais de Sistema

### Segurança
- **[NOVO]** Implementar rate limiting nas APIs
- **[NOVO]** Log de auditoria em todas as ações críticas
- **[NOVO]** Backup automático antes de importações grandes

### Performance
- **[NOVO]** Indexação adequada no banco para relatórios
- **[NOVO]** Paginação em todas as listagens
- **[NOVO]** Cache para dados frequentemente acessados

### UX/UI
- **[NOVO]** Loading states para operações longas
- **[NOVO]** Feedback visual imediato para ações do usuário
- **[NOVO]** Tour guiado para novos usuários

### Funcionalidades Futuras (Backlog)
- **[NOVO]** Mobile responsivo: Vendedores precisam acessar em campo
- **[NOVO]** Integração com WhatsApp/Telefonia: Para registro automático de interações
- **[NOVO]** Backup/Restore: Plano de contingência
- **[NOVO]** Multi-tenancy: Se planeja SaaS futuramente

---

## Resumo de Novos Requisitos Adicionados na v8.4
- 23 novos requisitos funcionais
- 15 novos requisitos técnicos
- 8 novos requisitos de segurança/performance/UX
- 4 funcionalidades para backlog futuro

**Total: 50 novos requisitos organizados e formalizados**

---

## 🏛️ Governança de Projeto e Documentação

### Controle de Versão e Documentação
- **[CRÍTICO]** Versionar este plano em Markdown no Git com changelog detalhado
  - Cada versão do plano deve ter tag no Git
  - Changelog deve incluir: novos requisitos, modificações, remoções
  - Histórico de decisões arquiteturais documentado

### Critérios de Pronto (Definition of Done)
- **[FUNDAMENTAL]** Definir critérios de pronto (DoD) específicos para cada versão:
  - **Código**: Testes unitários, code review, documentação
  - **Funcional**: Testes de aceitação, validação com stakeholders
  - **Técnico**: Performance, segurança, compatibilidade
  - **Deploy**: Ambiente de homologação testado, rollback plan

### Especificação Técnica
- **[ESSENCIAL]** Iniciar especificação de API REST baseada nos módulos:
  - Documentação OpenAPI/Swagger para cada endpoint
  - Exemplos de request/response
  - Códigos de erro padronizados
  - Versionamento de API (v1, v2, etc.)

### Modelagem de Dados
- **[FUNDAMENTAL]** Mapear entidades de dados e relacionamentos (ERD):
  - Diagrama ER completo do sistema
  - Dicionário de dados detalhado
  - Scripts de migração versionados
  - Políticas de backup e retenção

### Processo de Release
- **[NOVO]** Implementar pipeline de release estruturado:
  - Ambiente de desenvolvimento → staging → produção
  - Testes automatizados em cada ambiente
  - Validação de performance antes do deploy
  - Comunicação de releases para usuários

### Métricas e Monitoramento
- **[NOVO]** Definir KPIs de desenvolvimento e produto:
  - Tempo de desenvolvimento por feature
  - Taxa de bugs em produção
  - Satisfação do usuário por funcionalidade
  - Performance e uptime do sistema

---