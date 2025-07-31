# CRM Azevix - Roadmap Organizado por Regras de Negócio

## 📋 **VERSÕES CONCLUÍDAS**
- **v1.0-2.2**: Autenticação, CRUD básico de Leads, estrutura inicial

---

## 🏗️ **FASE 1: FUNDAÇÃO DE DADOS**

### **v2.03: Estrutura Empresarial**
**Regra de Negócio**: Todo negócio acontece com empresas e pessoas específicas
- Entidades Conta (empresa) e Contato (pessoa) como base do sistema
- CNPJ como identificador único para evitar duplicatas
- Validação e criptografia de dados sensíveis
- Soft delete para preservar histórico

### **v2.04: Visão 360° do Cliente**
**Regra de Negócio**: Centralizar todas as informações do cliente em um só lugar
- Página de detalhes da conta como hub central
- Visualização de todos os contatos e oportunidades por empresa
- Gestão de múltiplos contatos por conta

### **v2.05-2.07: Hierarquia Empresarial**
**Regra de Negócio**: Empresas podem ter matriz/filial e responsáveis específicos
- Relacionamento matriz-filial entre contas
- Atribuição de vendedores responsáveis
- Ciclo de vida completo (ativar/desativar) com tratamento de órfãos

---

## 👥 **FASE 2: GESTÃO DE EQUIPES**

### **v3.0: Sistema de Permissões**
**Regra de Negócio**: Diferentes usuários têm diferentes níveis de acesso
- Papéis definidos: Admin, Gerente, Vendedor
- Hierarquia de equipes (gerente → vendedores)
- Estrutura de banco preparada para permissões

### **v3.1: Onboarding Seguro**
**Regra de Negócio**: Controle total sobre quem pode acessar o sistema
- Primeiro usuário vira admin automaticamente
- Convites por e-mail com tokens seguros
- Autogestão de perfil e senha

### **v3.2: Visibilidade por Hierarquia**
**Regra de Negócio**: Cada usuário vê apenas o que deve ver
- Admin vê tudo
- Gerente vê sua equipe
- Vendedor vê apenas seus clientes
- Soft delete para usuários

---

## 📊 **FASE 3: GESTÃO DE OPORTUNIDADES**

### **v4.01: Auditoria e Performance**
**Regra de Negócio**: Rastrear mudanças importantes e manter sistema ágil
- Log de alterações em entidades críticas
- Paginação em todas as listas

### **v5.03: Enriquecimento do Pipeline**
**Regra de Negócio**: Vendas seguem estágios e precisam de follow-up
- Campos: estágio, motivo de perda, temperatura, follow-up necessário
- Auditoria automática de mudanças de status

### **v6.0: Central de Leads** ⭐ **VERSÃO ATUAL**
**Regra de Negócio**: Leads sem dono ficam em pool comum, cada vendedor gerencia os seus
- Pool de leads disponíveis para toda equipe
- Sistema de "assumir lead"
- Filtros por estágio, status e follow-up
- Métricas básicas de performance

### **v6.1: Gestão para Líderes**
**Regra de Negócio**: Gerentes podem reatribuir leads e acompanhar equipe
- Visão de leads da equipe para gerentes
- Funcionalidade de reatribuição
- Sistema de notificações

---

## ⚙️ **FASE 4: CONFIGURAÇÃO E ADMINISTRAÇÃO**

### **v7.0-7.1: Configurações Centralizadas**
**Regra de Negócio**: Admin controla identidade da empresa e fluxo de convites
- Configurações da empresa (nome, dados, SMTP)
- Domínios de e-mail permitidos
- Fluxo completo de convite de usuários

### **v8.0-8.2: Importação de Dados**
**Regra de Negócio**: Migração de dados externos deve ser segura e rastreável
- Upload e processamento de CSV
- Validação de duplicatas e consistência
- Histórico e auditoria de importações
- Processamento assíncrono para grandes volumes

---

## 🔄 **FASE 5: WORKFLOW INTELIGENTE**

### **v9.0: Configuração do Funil** 
**Regra de Negócio**: Admin define os estágios e regras do processo de vendas
- Gestão de Status, Motivos de Perda e Segmentos
- Flags especiais (status de perda, status inicial)

### **v9.1: Definição de Transições**
**Regra de Negócio**: Vendas seguem fluxo definido, não podem pular etapas
- Mapeamento de transições permitidas entre status
- Regras salvas no banco de dados

### **v9.2: Aplicação do Workflow** 🚀 **PRÓXIMA VERSÃO**
**Regra de Negócio**: Sistema guia vendedor no processo correto
- Interface mostra apenas próximos status válidos
- Validação de transições no backend
- Exigência de motivo quando lead é perdido

### **v9.3: Configuração Rápida**
**Regra de Negócio**: Acelerar onboarding de novos admins com padrões de mercado
- Botão "Aplicar Padrão do Sistema" para popular configurações automaticamente
- Templates prontos de status, motivos e workflow típicos de CRM
- Elimina necessidade de configurar tudo do zero

---

## 💰 **FASE 6: COMERCIALIZAÇÃO**

### **v10.0: Catálogo de Produtos**
**Regra de Negócio**: Padronizar produtos/serviços com preços e categorias
- Gestão centralizada do catálogo
- Categorização e regras de desconto
- Produtos combo/bundle

### **v11.0: Propostas Estruturadas**
**Regra de Negócio**: Propostas formais com cálculo de margem e versionamento
- Propostas com múltiplos produtos do catálogo
- Cálculo automático de custos e margem
- Controle de versões e status

### **v12.0: Automação de Documentos**
**Regra de Negócio**: Gerar e enviar propostas profissionais automaticamente
- PDF personalizado com branding da empresa
- Envio por e-mail direto do sistema
- Assinatura digital e tracking

---

## 📈 **FASE 7: GESTÃO OPERACIONAL**

### **v13.0: Atividades e Tarefas**
**Regra de Negócio**: Organizar e acompanhar todas as interações com clientes
- Gestão de tarefas por tipo e prioridade
- Lembretes automáticos
- Integração com calendário

### **v14.0: Relatórios e Inteligência**
**Regra de Negócio**: Decisões baseadas em dados e métricas de performance
- Dashboard com funil visual
- Relatórios exportáveis e agendáveis
- Métricas de conversão e performance

---

## 🎯 **STATUS ATUAL**
- **Concluído até**: v6.0 (Central de Leads)
- **Em desenvolvimento**: v9.2 (Aplicação do Workflow)
- **Próximo marco**: Workflow inteligente funcionando 100%