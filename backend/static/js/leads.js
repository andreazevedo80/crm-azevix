document.addEventListener("DOMContentLoaded", function() {
    // --- ELEMENTOS DA PÁGINA ---
    const container = document.getElementById('leads-table-container');
    const paginationContainer = document.getElementById('pagination-container');
    const searchInput = document.getElementById('lead-search-input');
    const meusLeadsTab = document.getElementById('filter-meus-leads');
    const poolTab = document.getElementById('filter-pool');
    const estagioFilter = document.getElementById('filter-estagio');
    const statusFilter = document.getElementById('filter-status');
    const temperaturaFilter = document.getElementById('filter-temperatura');
    const followupFilter = document.getElementById('filter-followup');
    // --- ADIÇÃO v6.1 ---
    const ownerFilter = document.getElementById('filter-owner');
    const statusCountersContainer = document.getElementById('status-counters-container');
    const reatribuirModalEl = document.getElementById('reatribuirLeadModal');
    const reatribuirModal = new bootstrap.Modal(reatribuirModalEl);
    const formReatribuirLead = document.getElementById('form-reatribuir-lead');

    const loadingSpinner = `<div class="text-center py-5"><div class="spinner-border text-azevix" role="status"></div></div>`;
    
    let currentPage = 1;
    let currentViewMode = 'meus_leads';
    let searchTimeout;

    // ALTERAÇÃO 1: Função populateSelect corrigida para lidar com lista de objetos
    const populateSelect = (selectElement, options, isObjectList = false) => {
        if (isObjectList) {
            options.forEach(opt => selectElement.add(new Option(opt.name, opt.id)));
        } else {
            options.forEach(opt => selectElement.add(new Option(opt, opt)));
        }
    };

    const populateFilters = async () => {
        try {
            const response = await fetch('/api/leads/config');
            const data = await response.json();
            if (data.success) {
                populateSelect(estagioFilter, data.estagios);
                populateSelect(statusFilter, data.status);
                populateSelect(temperaturaFilter, data.temperaturas);
            }
            // --- ADIÇÃO v6.1: Popula o filtro de responsáveis para admin/gerente ---
            if ((IS_ADMIN || IS_MANAGER) && ownerFilter) {
                const adminDataRes = await fetch('/api/admin/form_data');
                const adminData = await adminDataRes.json();
                if (adminData.success) {
                    // ALTERAÇÃO 2: Corrigido para usar isObjectList = true para vendedores
                    populateSelect(ownerFilter, adminData.vendedores, true);
                }
            }
        } catch (error) { console.error("Erro ao carregar filtros:", error); }
    };

    // --- ADIÇÃO v6.1: Função para buscar e renderizar contadores de status ---
    // ALTERAÇÃO 3: fetchAndRenderStats agora envia o view_mode para a API
    const fetchAndRenderStats = () => {
        if (!statusCountersContainer) return;
        fetch(`/api/leads/stats?view_mode=${currentViewMode}`)
            .then(res => res.json())
            .then(data => {
                if(data.success) {
                    statusCountersContainer.innerHTML = '';
                    for (const [status, count] of Object.entries(data.stats)) {
                        const badge = document.createElement('span');
                        // ALTERAÇÃO: Classe CSS alterada para bg-primary (melhoria visual)
                        badge.className = 'badge rounded-pill bg-primary p-2';
                        badge.style.cursor = 'pointer';
                        badge.textContent = `${status} (${count})`;
                        badge.onclick = () => {
                            statusFilter.value = status;
                            applyFiltersAndSearch();
                        };
                        statusCountersContainer.appendChild(badge);
                    }
                }
            });
    };

    const renderPagination = (pagination) => {
        paginationContainer.innerHTML = '';
        if (!pagination || pagination.pages <= 1) return;

        let paginationHTML = '<ul class="pagination mb-0">';
        paginationHTML += `<li class="page-item ${!pagination.has_prev ? 'disabled' : ''}"><a class="page-link" href="#" data-page="${pagination.page - 1}">Anterior</a></li>`;
        for (let i = 1; i <= pagination.pages; i++) {
            paginationHTML += `<li class="page-item ${i === pagination.page ? 'active' : ''}"><a class="page-link" href="#" data-page="${i}">${i}</a></li>`;
        }
        paginationHTML += `<li class="page-item ${!pagination.has_next ? 'disabled' : ''}"><a class="page-link" href="#" data-page="${pagination.page + 1}">Próximo</a></li>`;
        paginationHTML += '</ul>';
        paginationContainer.innerHTML = paginationHTML;

        paginationContainer.querySelectorAll('.page-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const newPage = e.target.dataset.page;
                if (newPage && currentPage !== parseInt(newPage)) {
                    currentPage = parseInt(newPage);
                    fetchAndRenderLeads();
                }
            });
        });
    };

    const renderLeads = (leads, pagination) => {
        let tableHTML = `
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>Oportunidade</th>
                        <th>Conta</th>
                        <th>Estágio</th>
                        <th>Status</th>
                        <th class="text-center">Temp.</th>
                        <th class="text-center">Follow-up</th>
                        <th>Responsável</th>
                        <th>Ações</th>
                    </tr>
                </thead>
                <tbody>`;
        
        if (leads.length > 0) {
            leads.forEach(lead => {
                const tempIcon = lead.temperatura === 'Quente' ? 'fa-fire text-danger' : (lead.temperatura === 'Frio' ? 'fa-snowflake text-info' : 'fa-sun text-warning');
                const followupIcon = lead.follow_up_necessario ? 'fa-flag text-danger' : 'fa-flag text-muted';
                
                let actionButton = `<a href="/contas/${lead.conta_id}" class="btn btn-sm btn-outline-secondary">Ver Conta</a>`;
                if (currentViewMode === 'pool') {
                    actionButton = `<button class="btn btn-sm btn-success" onclick="assumirLead(${lead.id})">Assumir</button>`;
                } else if (IS_ADMIN || IS_MANAGER) {
                    // --- ADIÇÃO v6.1: Adiciona o botão de Reatribuir ---
                    actionButton += ` <button class="btn btn-sm btn-outline-info ms-1" onclick="openReatribuirModal(${lead.id}, '${lead.titulo}')" title="Reatribuir"><i class="fas fa-exchange-alt"></i></button>`;
                }

                tableHTML += `
                    <tr>
                        <td><strong>${lead.titulo}</strong></td>
                        <td><a href="/contas/${lead.conta_id}">${lead.conta_nome}</a></td>
                        <td><span class="badge bg-primary">${lead.estagio_ciclo_vida}</span></td>
                        <td><span class="badge bg-info">${lead.status_lead}</span></td>
                        <td class="text-center"><i class="fas ${tempIcon} fa-lg" title="${lead.temperatura}"></i></td>
                        <td class="text-center"><i class="fas ${followupIcon} fa-lg"></i></td>
                        <td>${lead.owner_name}</td>
                        <td>${actionButton}</td>
                    </tr>`;
            });
        } else {
            tableHTML += '<tr><td colspan="8" class="text-center">Nenhum lead encontrado.</td></tr>';
        }
        tableHTML += '</tbody></table>';
        container.innerHTML = tableHTML;
        renderPagination(pagination);
    };
    
    // --- ADIÇÃO v6.0: Função para assumir um lead ---
    window.assumirLead = (leadId) => {
        if (!confirm('Tem certeza que deseja assumir esta oportunidade? Ela e a conta associada serão movidas para a sua carteira.')) return;

        fetch(`/api/leads/${leadId}/assumir`, { method: 'POST' })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    meusLeadsTab.click(); // Move para a aba "Minhas Oportunidades" e recarrega
                } else {
                    alert(`Erro: ${data.error || 'Não foi possível assumir o lead.'}`);
                    fetchAndRenderLeads(); // Recarrega a aba do pool
                }
            });
    };

    const fetchAndRenderLeads = () => {
        container.innerHTML = loadingSpinner;
        const params = new URLSearchParams({
            page: currentPage,
            view_mode: currentViewMode,
            search: searchInput.value,
            estagio: estagioFilter.value,
            status: statusFilter.value,
            temperatura: temperaturaFilter.value,
            followup: followupFilter.checked,
        });
        // --- CORREÇÃO: Garante que o valor do filtro de owner seja adicionado corretamente ---
        if ((IS_ADMIN || IS_MANAGER) && ownerFilter && ownerFilter.value) {
            params.append('owner_id', ownerFilter.value);
        }

        fetch(`/api/leads?${params.toString()}`)
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    renderLeads(data.leads, data.pagination);
                }
            });
    };

    const applyFiltersAndSearch = () => {
        currentPage = 1;
        fetchAndRenderLeads();
    };

    // --- ADIÇÃO v6.1: Lógica para Reatribuir Lead ---
    window.openReatribuirModal = (leadId, leadTitulo) => {
        formReatribuirLead.querySelector('#reatribuir-lead-id').value = leadId;
        formReatribuirLead.querySelector('#reatribuir-lead-titulo').textContent = leadTitulo;
        
        // Popula o select com os mesmos vendedores do filtro principal
        const selectOwner = formReatribuirLead.querySelector('#select-novo-owner');
        selectOwner.innerHTML = ownerFilter.innerHTML;
        selectOwner.value = ''; // Reseta a seleção

        reatribuirModal.show();
    };

    formReatribuirLead.addEventListener('submit', (e) => {
        e.preventDefault();
        const leadId = formReatribuirLead.querySelector('#reatribuir-lead-id').value;
        const newOwnerId = formReatribuirLead.querySelector('#select-novo-owner').value;

        if (!newOwnerId) {
            alert('Por favor, selecione um novo responsável.');
            return;
        }

        fetch(`/api/leads/${leadId}/reatribuir`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ new_owner_id: newOwnerId })
        })
        .then(res => res.json())
        .then(data => {
            if(data.success) {
                reatribuirModal.hide();
                fetchAndRenderLeads();
            } else {
                alert(`Erro: ${data.error}`);
            }
        });
    });

    meusLeadsTab.addEventListener('click', (e) => {
        e.preventDefault();
        currentViewMode = 'meus_leads';
        meusLeadsTab.classList.add('active');
        poolTab.classList.remove('active');
        applyFiltersAndSearch();
        // ALTERAÇÃO 4: Chama fetchAndRenderStats quando muda de aba
        fetchAndRenderStats();
    });

    poolTab.addEventListener('click', (e) => {
        e.preventDefault();
        currentViewMode = 'pool';
        poolTab.classList.add('active');
        meusLeadsTab.classList.remove('active');
        applyFiltersAndSearch();
        // ALTERAÇÃO 4: Chama fetchAndRenderStats quando muda de aba
        fetchAndRenderStats();
    });

    searchInput.addEventListener('keyup', () => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(applyFiltersAndSearch, 500);
    });
    
    [estagioFilter, statusFilter, temperaturaFilter, followupFilter].forEach(el => {
        el.addEventListener('change', applyFiltersAndSearch);
    });
    if (ownerFilter) {
        ownerFilter.addEventListener('change', applyFiltersAndSearch);
    }
    // --- INICIALIZAÇÃO ---
    const init = async () => {
        await populateFilters();
        fetchAndRenderLeads();
        // --- ADIÇÃO v6.1: Busca os contadores ---
        fetchAndRenderStats();
    };
    
    init();
});