
# 📊 CRM Azevix

**CRM Azevix** é um sistema de gerenciamento de relacionamento com clientes voltado para empresas que desejam ter controle completo sobre contas, contatos, leads, propostas e funil de vendas. Ele foi desenvolvido com foco em **segurança, escalabilidade e personalização**.

---

## 🚀 Visão Geral

Este projeto busca entregar um CRM profissional e personalizável, incorporando os melhores conceitos de arquitetura de dados:

- **Conta**: Entidade central que representa uma empresa ou órgão público.
- **Contato**: Pessoas que trabalham em uma conta (ex: gerente, financeiro, etc.).
- **Lead (Oportunidade)**: Potencial de negócio associado a uma conta e opcionalmente a um contato.

---

## 🧱 Arquitetura de Dados

| Entidade | Descrição |
|----------|-----------|
| **Conta** | Nome Fantasia, Razão Social, CNPJ (criptografado), Tipo de Conta |
| **Contato** | Nome, E-mail, Telefone, Cargo — sempre vinculado a uma Conta |
| **Lead** | Representa uma oportunidade de negócio — ligada a uma Conta e opcionalmente a um Contato |
| **Usuário** | Possui permissões (roles) que controlam o acesso às entidades |
| **Proposta** | Ligada a um Lead, com produtos/serviços, custos e estimativa de lucro |

---

## 🛡️ Princípios do Projeto

- ✅ **Fonte Única da Verdade**: Nada de valores hardcoded — configurações são armazenadas no banco.
- ✅ **Segurança em Primeiro Lugar**: Controle de acesso, criptografia, soft delete, domínio verificado.
- ✅ **Escalabilidade**: Com uso de paginação, índices e arquitetura modular.
- ✅ **Flexibilidade**: Admins podem configurar status, segmentos, workflow e SMTP diretamente pelo painel.

---

## 📅 Roadmap de Desenvolvimento

### ✅ Versões Concluídas
- **1.0** – Autenticação e estrutura base
- **2.0 a 2.2** – CRUD de Leads, associação com vendedor, tipo de conta

### 🔄 Em Desenvolvimento

#### `v2.03` – **Reestruturação: Contas, Contatos e Validações**
- CNPJ validado e criptografado
- Soft delete e padronização de dados
- Normalização de nomes e telefones

#### `v2.04` – **Segurança e Permissões (Roles)**
- Controle de acesso por papéis (admin, vendedor, etc.)
- Convites apenas para domínios autorizados (configurável)

#### `v2.05` – **Log de Auditoria e Paginação**
- Histórico de alterações por entidade
- Paginação de listas (Leads, Contas, etc.)

#### `v3.01` – **Administração e Workflow Inteligente**
- CRUD de Status, Segmentos e Motivos de Perda
- Regras de transição de status

#### `v4.01` – **Módulo de Propostas**
- Estrutura completa: itens, custos, lucro estimado
- Catálogo de produtos e serviços

#### `v4.02` – **Automação de Documentos e Comunicação**
- Geração de proposta em PDF
- Envio de e-mails com SMTP personalizado

#### `v5.01` – **Dashboard e Relatórios**
- Funil de vendas dinâmico
- Relatórios por vendedor, data, status
- Exportação em PDF

---

## 🛠️ Tecnologias

| Camada | Tecnologias |
|--------|-------------|
| Backend | Python 3.11, Flask, SQLAlchemy, PostgreSQL |
| Frontend | HTML, Jinja2, JavaScript, Bootstrap |
| Infraestrutura | Docker, Docker Compose, Nginx |
| Documentação | Markdown, Roadmap |

---

## 📂 Organização do Projeto

O projeto segue uma arquitetura modular com Flask Blueprints.

```
🔄 Em Desenvolvimento
crm-azevix/
├── backend/
│   ├── __init__.py
│   ├── auth.py
│   ├── leads.py
│   ├── main.py
│   ├── models.py
│   ├── static/
│   │   ├──css
│   │   │   └──main.cs
│   │   └──js
│   │      ├──leads.js
│   │      └──novo_lead.js
│   └── templates/
│       ├── base.html
│       ├── dashboard.html
│       ├── leads.html
│       ├── login.html
│       ├── novo_lead.html
│       └── register.html
├── .env
├── .env.example
├── .gitignore
├── Dockerfile
├── README.md
├── boot.sh
├── docker-compose.yml
├── nginx.conf
├── requirements.txt
└── run.py

```

---

## 📦 Como Executar Localmente

### Pré-requisitos
- Crie um arquivo .env a partir do .env.example e preencha com seus valores
- Docker e Docker Compose instalados

### Passos

```bash
# Clone o repositório
git clone https://github.com/andreazevedo80/crm-azevix.git
cd crm-azevix

# Suba os containers
docker-compose up --build
```

Acesse o sistema em `http://localhost`.

---

## 📃 Licença

Este projeto está licenciado sob os termos da **MIT License**.

---

## 🤝 Contribuição

Pull requests são bem-vindos. Se você tiver sugestões, abra uma [issue](https://github.com/andreazevedo80/crm-azevix/issues).

---

## 👨‍💻 Autor

Desenvolvido por **André Azevedo**  
[LinkedIn](https://www.linkedin.com/in/andreazevedo1980/) • [Site pessoal](https://azevix.com.br)
