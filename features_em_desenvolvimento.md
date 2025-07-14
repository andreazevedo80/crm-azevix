### Plano de Ação e Requisitos de Software - CRM Azevix (Revisão Final)

## versão 2.07 [Finalização da Gestão de Contas]
# Objetivo
- Concluir o ciclo de vida completo da entidade Conta, permitindo a desativação de contatos e a gestão segura da hierarquia.

# Requisitos da feature:
- Um admin/gerente/vendedor poderá "excluir" (desativar)  e "editar" um contato da página de detalhes da conta.
- Um admin/gerente poderá "excluir" (desativar) um contato da página de detalhes da conta.
- A busca por "Conta Matriz" (tanto no cadastro quanto na edição) deve impedir que uma conta seja definida como sua própria matriz.


# O que será modificado:
- backend/models.py: Adicionar a regra ondelete='SET NULL' no relacionamento matriz_id.
- backend/contas.py: Adicionar a rota DELETE /api/contatos/<int:id> e a lógica para desativação de contas e tratamento de filiais.
- backend/static/js/detalhe_conta.js: Adicionar a lógica para o botão de exclusão de contato e o filtro na busca por matriz.

## versão 2.08 [Segurança, Permissões e Hierarquia de Usuários]
# Objetivo
- Implementar um sistema de permissões robusto com diferentes papéis (Roles), uma estrutura de gestão de equipes e um fluxo de cadastro seguro.

# Requisitos da feature:
- O sistema deve ter uma tabela Role no banco para armazenar os papéis ('admin', 'gerente', 'vendedor'). (JÁ TEM)
- O modelo User será refatorado para usar um relacionamento com a tabela Role e terá um campo gerente_id para a hierarquia de equipes.
- A tela de registro público será desativada após o primeiro usuário (o admin) ser criado.
- Admins e Gerentes poderão convidar novos usuários através de um link seguro enviado por e-mail.
- No envio de convite, terá expiração automática e talvez um uso único (token + tempo).
- A API de listagem de Contas respeitará a role: admin vê tudo, gerente vê sua equipe, vendedor vê apenas o seu.
- Todos os usuários terão uma página /perfil para alterar a própria senha.
- A lógica de negócio para tratar filiais órfãs (quando uma matriz for desativada) será implementada.

# O que será modificado:
- backend/models.py: Criar a tabela Role e refatorar o modelo User.
- backend/auth.py: Implementar a lógica de "primeiro admin" e o novo fluxo de convite.
- backend/user.py (Novo): Criar o Blueprint e a tela para o perfil do usuário.
- backend/email.py (Novo): Criar o módulo para envio de e-mails.
- backend/contas.py e backend/templates/: Ajustar todas as verificações de permissão para usar o novo sistema has_role('admin').

## versão 2.09 [Log de Auditoria e Paginação]
# Objetivo
- Rastrear alterações importantes e garantir a performance do sistema.

# Requisitos da feature:
- O sistema deve registrar um histórico de alterações para entidades críticas como Lead e Proposta.
- Todas as listas principais devem ser paginadas para manter a aplicação rápida.

# O que será modificado:
- backend/models.py: Criar a tabela HistoricoAlteracao.
- backend/contas.py, backend/propostas.py: Adicionar a lógica para registrar o histórico nas rotas de atualização.
- backend/static/js/ e backend/*_api.py: Implementar a lógica de paginação no frontend e backend.

## versão 3.01 [Módulo de Administração Centralizado]
# Objetivo
- Dar ao administrador controle total sobre as regras de negócio e configurações do sistema.

# Requisitos da feature:
- Admin pode gerenciar (CRUD) os Status de Lead, Segmentos, Motivos de Perda.
- Admin pode definir o Workflow de Status (regras de transição).
- Admin pode gerenciar as configurações de e-mail (SMTP) e os domínios permitidos para convite.

# O que será modificado:
- backend/models.py: Criar as tabelas de configuração (ConfigStatusLead, ConfigSegmento, etc.).
- backend/admin.py (Novo): Criar o Blueprint e as interfaces do painel de administração.

## versão 4.01 [Propostas: Estrutura, Custos e Lucratividade]
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

# versão 4.02 [Automação de Documentos e Comunicação]
# Objetivo
- Automatizar a criação e o envio de propostas.

# Requisitos da feature:
- O sistema deve gerar um documento PDF profissional e personalizável a partir dos dados de uma proposta.
- Deve ser possível enviar a proposta gerada por e-mail diretamente do sistema, usando o e-mail configurado do vendedor.
- Se possível, permita customização de template do PDF por empresa (branding).

# O que será modificado:
- backend/propostas.py: Adicionar a rota para geração de PDF e a lógica de envio de e-mail.
- backend/email.py (Novo): Módulo utilitário para envio de e-mails, lendo as configurações do banco de dados.

# versão 5.01 [Módulo de Relatórios e Dashboard Inteligente]
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