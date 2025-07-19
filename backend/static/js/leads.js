document.addEventListener("DOMContentLoaded", function() {
    const container = document.getElementById('leads-table-container');
    const paginationContainer = document.getElementById('pagination-container');
    const searchInput = document.getElementById('lead-search-input');
    const meusLeadsTab = document.getElementById('filter-meus-leads');
    const poolTab = document.getElementById('filter-pool');
    const estagioFilter = document.getElementById('filter-estagio');
    const statusFilter = document.getElementById('filter-status');
    const temperaturaFilter = document.getElementById('filter-temperatura');
    const followupFilter = document.getElementById('filter-followup');

    const loadingSpinner = `<div class="text-center py-5"><div class="spinner-border text-azevix" role="status"></div></div>`;
    
    let currentPage = 1;
    let currentViewMode = 'meus_leads';
    let searchTimeout;

    const populateSelect = (selectElement, options) => {
        options.forEach(opt => selectElement.add(new Option(opt, opt)));
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
        } catch (error) { console.error("Erro ao carregar filtros:", error); }
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
    
    const fetchAndRenderLeads = () => {
        container.innerHTML = loadingSpinner;
        const params = new URLSearchParams({
            page: currentPage,
            view_mode: currentViewMode,
            search: searchInput.value,
            estagio: estagioFilter.value,
            status: statusFilter.value,
            temperatura: temperaturaFilter.value,
            followup: followupFilter.checked
        });

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

    meusLeadsTab.addEventListener('click', (e) => {
        e.preventDefault();
        currentViewMode = 'meus_leads';
        meusLeadsTab.classList.add('active');
        poolTab.classList.remove('active');
        applyFiltersAndSearch();
    });

    poolTab.addEventListener('click', (e) => {
        e.preventDefault();
        currentViewMode = 'pool';
        poolTab.classList.add('active');
        meusLeadsTab.classList.remove('active');
        applyFiltersAndSearch();
    });

    searchInput.addEventListener('keyup', () => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(applyFiltersAndSearch, 500);
    });
    
    [estagioFilter, statusFilter, temperaturaFilter, followupFilter].forEach(el => {
        el.addEventListener('change', applyFiltersAndSearch);
    });

    const init = async () => {
        await populateFilters();
        fetchAndRenderLeads();
    };
    
    init();
});