### Plano de Ação e Requisitos de Software - CRM Azevix (Revisão 5.0)

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

## versão 5.01 [Módulo de Administração Centralizado]
# Objetivo
- Dar ao administrador controle total sobre as regras de negócio e configurações do sistema.

# Requisitos da feature:
- Admin pode gerenciar (CRUD) os Status de Lead, Segmentos, Motivos de Perda.
- Admin pode definir o Workflow de Status (regras de transição).
- Admin pode gerenciar as configurações de e-mail (SMTP) e os domínios permitidos para convite.

# O que será modificado:
- backend/models.py: Criar as tabelas de configuração (ConfigStatusLead, ConfigSegmento, etc.).
- backend/admin.py (Novo): Criar o Blueprint e as interfaces do painel de administração.

## versão 6.01 [Propostas: Estrutura, Custos e Lucratividade]
# Objetivo
- Implementar o módulo de propostas, o coração financeiro do CRM.

# Requisitos da feature:
- Ser capaz de criar propostas detalhadas, com múltiplos produtos/serviços de um catálogo.
- Adicionar custos (fixos/percentuais) para calcular a margem de lucro estimada.
- A lógica de custos deve ser sensível ao tipo_conta (Pública vs. Privada).
- Propostas devem ter status e prazos.

# O que será modificado:
- backend/models.py: Criar as tabelas ProdutoServico, Proposta, ItemProposta, CustoProposta.
- backend/propostas.py (Novo): Blueprint com toda a lógica de negócio para propostas.
- backend/templates/: Novas interfaces para criar e visualizar propostas.

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