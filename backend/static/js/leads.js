document.addEventListener("DOMContentLoaded", function() {
    
    // Mapeamento de todos os elementos da página
    const elements = {
        displayArea: document.getElementById('leads-display-area'),
        searchInput: document.getElementById('search-filter'),
        statusFilter: document.getElementById('status-filter'),
        segmentFilter: document.getElementById('segment-filter'),
        checkModalInput: document.getElementById('check-company-name'),
        checkResultsContainer: document.getElementById('check-results-container'),
        proceedButton: document.getElementById('proceed-to-register-btn'),
        checkModalEl: document.getElementById('checkLeadModal'),
        editModalEl: document.getElementById('editLeadModal'),
        editLeadForm: document.getElementById('editLeadForm'),
        editLeadId: document.getElementById('edit-lead-id'),
        editNomeConta: document.getElementById('edit-nome_conta'),
        editNomeCompleto: document.getElementById('edit-nome_completo'),
        editEmail: document.getElementById('edit-email'),
        editTelefone: document.getElementById('edit-telefone_celular'),
        editSegmento: document.getElementById('edit-segmento'),
        editStatus: document.getElementById('edit-status_lead'),
        editObservacoes: document.getElementById('edit-observacoes'),
    };
    const editModal = new bootstrap.Modal(elements.editModalEl);

    // Template do spinner de loading
    const loadingSpinner = `<div class="text-center py-5"><div class="spinner-border text-azevix" role="status"></div></div>`;

    // Função para popular selects (filtros e modal)
    const populateSelect = async (selectElement, options) => {
        while (selectElement.options.length > 1) selectElement.remove(1); // Limpa mantendo o default
        options.forEach(opt => selectElement.add(new Option(opt, opt)));
    };

    // Busca as configurações da API e popula todos os selects
    const fetchConfigsAndPopulateAllFilters = async () => {
        try {
            const response = await fetch('/api/config');
            const data = await response.json();
            if (data.success) {
                await populateSelect(elements.statusFilter, data.status_leads);
                await populateSelect(elements.segmentFilter, data.segmentos);
                await populateSelect(elements.editStatus, data.status_leads);
                await populateSelect(elements.editSegmento, data.segmentos);
            }
        } catch (error) { console.error('Erro ao carregar configurações:', error); }
    };
    
    // Função principal que busca e renderiza a tabela de leads
    const fetchAndRenderLeads = () => {
        elements.displayArea.innerHTML = loadingSpinner;
        const params = new URLSearchParams({
            search: elements.searchInput.value,
            status: elements.statusFilter.value,
            segmento: elements.segmentFilter.value
        });

        fetch(`/api/leads?${params.toString()}`)
            .then(res => res.json())
            .then(data => {
                let tableContent = '';
                if (data.success && data.leads.length > 0) {
                    const rows = data.leads.map(lead => {
                        // Formata a data para o padrão brasileiro
                        const dataCadastro = new Date(lead.data_cadastro).toLocaleDateString('pt-BR');
                        return `
                        <tr>
                            <td>${lead.nome_completo}</td>
                            <td>${lead.nome_conta}</td>
                            <td>${lead.segmento}</td>
                            <td><span class="badge bg-primary">${lead.status_lead}</span></td>
                            <td>${dataCadastro}</td>
                            <td>${lead.owner_name}</td>
                            <td>
                                <button class="btn btn-sm btn-outline-primary" onclick="openEditModal(${lead.id})"><i class="fas fa-edit"></i></button>
                                <button class="btn btn-sm btn-outline-danger" onclick="handleDeleteLead(${lead.id})"><i class="fas fa-trash"></i></button>
                            </td>
                        </tr>`;
                    }).join('');
                    tableContent = `
                        <div class="table-responsive">
                            <table class="table table-hover">
                                <thead><tr><th>Contato</th><th>Empresa</th><th>Segmento</th><th>Status</th><th>Data Cadastro</th><th>Responsável</th><th>Ações</th></tr></thead>
                                <tbody>${rows}</tbody>
                            </table>
                        </div>`;
                } else {
                    tableContent = `<p class="text-center py-4">Nenhum lead encontrado.</p>`;
                }
                elements.displayArea.innerHTML = tableContent;
            });
    };

    // --- Funções Globais (chamadas pelo onclick no HTML) ---
    window.openEditModal = async (leadId) => {
        const response = await fetch(`/api/leads/${leadId}`);
        const data = await response.json();
        if (data.success) {
            const lead = data.lead;
            elements.editLeadId.value = lead.id;
            elements.editNomeConta.value = lead.nome_conta;
            elements.editNomeCompleto.value = lead.nome_completo;
            elements.editEmail.value = lead.email || '';
            elements.editTelefone.value = lead.telefone_celular || '';
            elements.editSegmento.value = lead.segmento;
            elements.editStatus.value = lead.status_lead;
            elements.editObservacoes.value = lead.observacoes || '';
            editModal.show();
        } else {
            alert('Erro ao carregar dados do lead.');
        }
    };

    window.handleDeleteLead = (leadId) => {
        if (confirm('Tem certeza que deseja excluir este lead?')) {
            fetch(`/api/leads/${leadId}`, { method: 'DELETE' })
                .then(res => res.json())
                .then(data => {
                    if (data.success) fetchAndRenderLeads();
                    else alert('Erro ao excluir o lead.');
                });
        }
    };
    
    // --- Event Listeners ---
    elements.editLeadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const leadId = elements.editLeadId.value;
        const updatedData = {
            nome_conta: elements.editNomeConta.value,
            nome_completo: elements.editNomeCompleto.value,
            email: elements.editEmail.value,
            telefone_celular: elements.editTelefone.value,
            segmento: elements.editSegmento.value,
            status_lead: elements.editStatus.value,
            observacoes: elements.editObservacoes.value,
        };

        const response = await fetch(`/api/leads/${leadId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updatedData)
        });
        const result = await response.json();
        if (result.success) {
            editModal.hide();
            fetchAndRenderLeads();
        } else {
            alert('Falha ao atualizar o lead.');
        }
    });

    // Adiciona os listeners aos filtros
    [elements.searchInput, elements.statusFilter, elements.segmentFilter].forEach(el => {
        el.addEventListener('change', fetchAndRenderLeads);
    });
    let searchTimeout;
    elements.searchInput.addEventListener('keyup', () => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(fetchAndRenderLeads, 500);
    });

    // Lógica do Modal de Verificação (código existente, sem alterações)
    const checkDuplicates = () => { /* ... */ };
    let checkTimeout;
    elements.checkModalInput.addEventListener('keyup', () => { clearTimeout(checkTimeout); checkTimeout = setTimeout(checkDuplicates, 500); });
    elements.checkModalEl.addEventListener('hidden.bs.modal', () => { /* ... */ });


    // --- INICIALIZAÇÃO DA PÁGINA ---
    const initPage = async () => {
        await fetchConfigsAndPopulateAllFilters(); // Espera os filtros serem preenchidos
        fetchAndRenderLeads(); // Depois busca os leads
    };
    initPage();
});