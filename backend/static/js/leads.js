document.addEventListener("DOMContentLoaded", function() {
    // === ELEMENTOS DA PÁGINA PRINCIPAL ===
    const loadingDiv = document.getElementById('loading');
    const tableContainer = document.getElementById('leads-table-container');
    const leadsListBody = document.getElementById('leads-list');
    const searchInput = document.getElementById('search-filter');
    const statusFilter = document.getElementById('status-filter');
    const segmentFilter = document.getElementById('segment-filter');

    // === ELEMENTOS DO MODAL DE VERIFICAÇÃO ===
    const checkModalInput = document.getElementById('check-company-name');
    const checkResultsContainer = document.getElementById('check-results-container');
    const proceedButton = document.getElementById('proceed-to-register-btn');

    // Função para popular os filtros de Status e Segmento
    const populateFilters = () => {
        fetch('/api/config')
            .then(response => response.json())
            .then(data => {
                if (!data.success) return;
                statusFilter.innerHTML = '<option value="">Todos os Status</option>';
                segmentFilter.innerHTML = '<option value="">Todos os Segmentos</option>';
                data.status_leads.forEach(status => statusFilter.add(new Option(status, status)));
                data.segmentos.forEach(seg => segmentFilter.add(new Option(seg, seg)));
            });
    };

    // Função para buscar e exibir a lista principal de leads
    const fetchLeads = () => {
        loadingDiv.style.display = 'block';
        tableContainer.style.display = 'none';

        const params = new URLSearchParams({
            search: searchInput.value,
            status: statusFilter.value,
            segmento: segmentFilter.value
        });

        fetch(`/api/leads?${params.toString()}`)
            .then(response => response.json())
            .then(data => {
                leadsListBody.innerHTML = '';
                if (data.success && data.leads.length > 0) {
                    data.leads.forEach(lead => {
                        leadsListBody.innerHTML += `
                            <tr>
                                <td>${lead.nome_completo}</td>
                                <td>${lead.nome_conta}</td>
                                <td>${lead.email || '-'}</td>
                                <td>${lead.telefone_celular || '-'}</td>
                                <td><span class="badge bg-primary">${lead.status_lead}</span></td>
                                <td>${lead.owner_name}</td>
                                <td><button class="btn btn-sm btn-outline-secondary" disabled>Editar</button></td>
                            </tr>`;
                    });
                } else {
                    leadsListBody.innerHTML = '<tr><td colspan="7" class="text-center">Nenhum lead encontrado.</td></tr>';
                }
            })
            .catch(error => console.error('Erro ao buscar leads:', error))
            .finally(() => {
                loadingDiv.style.display = 'none';
                tableContainer.style.display = 'block';
            });
    };
    
    // Função para checar duplicatas no modal
    const checkDuplicates = () => {
        const searchTerm = checkModalInput.value;
        proceedButton.style.display = 'none'; // Esconde o botão de prosseguir

        if (searchTerm.length < 3) {
            checkResultsContainer.innerHTML = '<p class="text-muted">Digite pelo menos 3 caracteres para iniciar a busca.</p>';
            return;
        }

        checkResultsContainer.innerHTML = '<div class="text-center"><div class="spinner-border spinner-border-sm" role="status"></div> Buscando...</div>';

        fetch(`/api/leads/check_duplicates?term=${encodeURIComponent(searchTerm)}`)
            .then(response => response.json())
            .then(data => {
                if (data.success && data.duplicates.length > 0) {
                    let resultsHtml = '<p><strong>Atenção!</strong> Empresas com nome similar já existem:</p><ul class="list-group">';
                    data.duplicates.forEach(lead => {
                        resultsHtml += `<li class="list-group-item"><strong>${lead.nome_conta}</strong> (Contato: ${lead.nome_completo} | Responsável: ${lead.owner_name})</li>`;
                    });
                    resultsHtml += '</ul>';
                    checkResultsContainer.innerHTML = resultsHtml;
                } else {
                    checkResultsContainer.innerHTML = '<p class="text-success">Nenhuma empresa encontrada com este nome. Você pode prosseguir.</p>';
                    proceedButton.style.display = 'inline-block'; // Mostra o botão para prosseguir
                }
            });
    };

    // --- EVENT LISTENERS ---

    // Filtros da página principal
    [searchInput, statusFilter, segmentFilter].forEach(element => {
        element.addEventListener('change', fetchLeads);
    });
    let searchTimeout;
    searchInput.addEventListener('keyup', () => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(fetchLeads, 500);
    });

    // Input de verificação no modal
    let checkTimeout;
    checkModalInput.addEventListener('keyup', () => {
        clearTimeout(checkTimeout);
        checkTimeout = setTimeout(checkDuplicates, 500);
    });
    
    // Limpa o modal quando ele é fechado
    const checkModalEl = document.getElementById('checkLeadModal');
    checkModalEl.addEventListener('hidden.bs.modal', function () {
        checkModalInput.value = '';
        checkResultsContainer.innerHTML = '';
        proceedButton.style.display = 'none';
    });


    // --- CARGA INICIAL ---
    populateFilters();
    fetchLeads();
});