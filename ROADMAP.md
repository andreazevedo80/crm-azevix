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

versão 7.0: Módulo de Administração (Configurações do Sistema)
Objetivo: Permitir que o administrador configure a "identidade" do sistema e as configurações de e-mail.
Requisitos:
Criar a nova tabela ConfigGlobal no models.py.
No painel de admin, criar uma nova página "Configurações Gerais".
Nesta página, implementar a interface para:
Configurações da Empresa (nome, endereço, etc.).
Configuração da URL Base do Site (SITE_URL).
Configuração do Servidor de E-mail (SMTP), com criptografia e botão de teste.

versão 7.1: Fluxo de Convite de Usuários
Objetivo: Habilitar o fluxo completo de convite de novos usuários.
Requisitos:
No painel de admin, criar uma nova página "Domínios Permitidos" para gerenciar os domínios de e-mail autorizados.
Na página de "Gestão de Usuários" (/admin/users), habilitar o botão "+Convidar Novo Usuário".
Ao clicar, um modal aparecerá pedindo o nome, e-mail e role do novo usuário.
Ao submeter, o backend irá:
Validar se o domínio do e-mail é permitido.
Criar o novo usuário com is_active = False.
Gerar o token de convite seguro.
Enviar o e-mail de convite usando as configurações de SMTP.

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

versão 8.0: Importação de Dados (MVP - Mínimo Produto Viável)
Objetivo: Entregar o fluxo essencial de importação de ponta a ponta, de forma síncrona.

Requisitos:

Criar a interface no painel de admin para upload de arquivos CSV.

Oferecer um template de CSV para download nesta página.

Implementar a lógica no backend para processar o arquivo, validar CNPJs duplicados e criar as Contas e Leads no "Lead Pool".

Ao final, gerar um relatório simples de sucessos e erros (ex: "Linha 5: CNPJ já existe").

O que entregamos aqui: A funcionalidade principal, que já agrega um valor imenso ao sistema.

versão 8.1: Importação de Dados (Usabilidade e Auditoria)
Objetivo: Refinar a experiência do administrador, tornando o processo mais seguro e rastreável.

Requisitos:

Implementar a funcionalidade de preview dos dados antes da importação final.

Implementar o histórico de importações (quem fez, quando, quantos registros, com um link para o relatório de erros).

Armazenar o arquivo CSV original associado ao histórico.

Adicionar validações mais robustas, como a de encoding do arquivo.

O que entregamos aqui: Uma experiência de importação mais segura e com total rastreabilidade.

versão 8.2: Importação de Dados (Performance e Segurança)
Objetivo: Preparar o módulo de importação para lidar com grandes volumes de dados de forma segura.

Requisitos:

Implementar o processamento assíncrono da importação. O admin fará o upload, o sistema começará a processar em segundo plano, e o admin será notificado (via e-mail ou notificação no sistema, em uma versão futura) quando terminar.

Backup Automático: Antes de iniciar um grande job de importação, o sistema poderia acionar um script de backup do banco de dados (esta é uma feature de infraestrutura complexa que podemos detalhar mais à frente).


---

## Versão 9.0: Workflow Inteligente de Vendas

### Requisitos Funcionais
- Interface para Admin gerenciar (CRUD) Status de Lead, Seguimentos e Motivos de Perda
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

versão 9.0: Administração de Entidades de Vendas
Objetivo: Dar ao admin o poder de customizar as peças do funil de vendas, eliminando as listas "hardcoded".
Requisitos:
Backend (models.py): Criar as novas tabelas: ConfigStatusLead, ConfigMotivosPerda e ConfigSegmento.
Backend (admin.py): Criar as novas rotas e APIs para o admin gerenciar (Adicionar, Editar, Desativar/Reativar) os Status, os Motivos de Perda e os Segmentos.
Refinamento do Status: Na interface de edição de um Status, adicionar os dois "flags" que discutimos:
[ ] É um status de perda?
[ ] É o status inicial após assumir um lead?
Frontend (admin/): Criar as novas páginas para o admin fazer a gestão de todas essas entidades.

versão 9.1: Definição do Workflow de Vendas
Objetivo: Permitir que o admin desenhe o processo do funil, definindo as conexões entre as peças que criamos na v9.0.
Requisitos:
Backend (models.py): Criar a nova tabela StatusTransicoes para armazenar as regras (ex: do status com ID 1, pode-se ir para os status com ID 2 e 5).
Interface do Admin: Na página de edição de um Status, adicionar uma nova seção com checkboxes onde o admin poderá selecionar quais são os "próximos status permitidos".
Backend (admin.py): Criar a API para salvar essas regras de transição na nova tabela.
O que entregamos aqui: As regras do processo de vendas estão salvas no banco de dados, prontas para serem usadas.

versão 9.2: Aplicação do Workflow na Interface do Vendedor
Objetivo: Fazer com que a interface do vendedor respeite e reforce o processo de vendas definido pelo administrador.
Requisitos:
Frontend (detalhe_conta.js): A lógica do modal de "Alterar Status" do lead será refatorada. Agora, o dropdown de status não mostrará mais todas as opções, mas sim apenas as transições permitidas a partir do status atual daquela oportunidade.
Backend (contas.py): A rota /api/leads/<id>/processo terá uma camada final de validação para garantir que a transição de status enviada pelo frontend é permitida pelas regras do workflow.
Frontend (detalhe_conta.js): A lógica para exigir o "Motivo de Perda" será implementada, aparecendo apenas quando o vendedor selecionar um status que foi marcado como "de perda".
O que entregamos aqui: O workflow inteligente está 100% funcional e visível para o usuário final, guiando a equipe de vendas no processo correto.

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

## 📋 Checklist de Implementação por Versão

### Template de DoD (aplicar para cada versão):
- [ ] **Desenvolvimento Completo**
  - [ ] Código implementado e revisado
  - [ ] Testes unitários com cobertura > 80%
  - [ ] Documentação técnica atualizada
  - [ ] Logs e monitoramento implementados

- [ ] **Testes e Qualidade**
  - [ ] Testes de integração executados
  - [ ] Testes de performance aprovados
  - [ ] Testes de segurança validados
  - [ ] Testes de aceitação do usuário (UAT)

- [ ] **Deploy e Infraestrutura**
  - [ ] Scripts de migração testados
  - [ ] Ambiente de staging validado
  - [ ] Plano de rollback definido
  - [ ] Monitoramento pós-deploy configurado

- [ ] **Documentação e Comunicação**
  - [ ] API documentation atualizada
  - [ ] Release notes preparadas
  - [ ] Treinamento de usuários realizado
  - [ ] Changelog do Git atualizado

**Total de novos requisitos: 54 (incluindo 4 de governança)**