# ADR 001: Centralização de Constantes de Configuração

**Data:** 2025-07-18

**Contexto:**
As listas de `STATUS_LEADS` e `SEGMENTOS` estavam "hardcoded" em `contas.py`. Com a criação do novo módulo `leads.py`, precisaríamos duplicar essas listas, o que é uma má prática e geraria problemas de manutenção.

**Decisão:**
Decidimos criar um novo arquivo central, `backend/config_constants.py`, para armazenar todas as listas de configuração "hardcoded". Os módulos que precisarem dessas listas (`contas.py`, `leads.py`, etc.) deverão importá-las deste arquivo.

**Consequências:**
* **Positivas:** Elimina a duplicação de código. Cria uma "fonte única da verdade" para as configurações. Facilita a manutenção.
* **Negativas:** Adiciona um novo arquivo ao projeto.