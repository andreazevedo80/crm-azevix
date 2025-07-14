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