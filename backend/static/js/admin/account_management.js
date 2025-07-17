document.addEventListener("DOMContentLoaded", function() {
    const activeFilter = document.getElementById('filter-active');
    const inactiveFilter = document.getElementById('filter-inactive');
    const container = document.getElementById('accounts-table-container');
    // --- ADIÇÃO v5.01.2: Elementos de busca e paginação ---
    const searchInput = document.getElementById('account-search-input');
    const paginationContainer = document.getElementById('pagination-container');
    
    let currentStatus = 'active';
    let currentPage = 1;
    let searchTimeout;

    const loadingSpinner = `<div class="text-center py-5"><div class="spinner-border text-azevix" role="status"></div></div>`;

    // --- ADIÇÃO v5.01.2: Nova função para renderizar paginação ---
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
                    fetchAndRenderAccounts();
                }
            });
        });
    };

    const fetchAndRenderAccounts = () => {
        container.innerHTML = loadingSpinner;
        // --- ALTERAÇÃO v5.01.2: Adiciona busca e paginação aos parâmetros ---
        const params = new URLSearchParams({
            status: currentStatus,
            page: currentPage,
            search: searchInput.value
        });

        fetch(`/admin/api/accounts?${params.toString()}`)
            .then(res => res.json())
            .then(data => {
                let tableHTML = '<table class="table table-hover"><thead><tr><th>Nome Fantasia</th><th>Responsável</th><th>Status</th><th>Ações</th></tr></thead><tbody>';
                if (data.success && data.contas.length > 0) {
                    data.contas.forEach(conta => {
                        tableHTML += `
                            <tr>
                                <td><a href="/contas/${conta.id}">${conta.nome_fantasia}</a></td>
                                <td>${conta.owner_name}</td>
                                <td><span class="badge bg-${currentStatus === 'active' ? 'success' : 'danger'}">${currentStatus === 'active' ? 'Ativa' : 'Inativa'}</span></td>
                                <td>
                                    ${currentStatus === 'inactive' ? `<button class="btn btn-sm btn-outline-success" onclick="reactivateAccount(${conta.id})">Reativar</button>` : ''}
                                </td>
                            </tr>`;
                    });
                } else {
                    tableHTML += '<tr><td colspan="4" class="text-center">Nenhuma conta encontrada.</td></tr>';
                }
                tableHTML += '</tbody></table>';
                container.innerHTML = tableHTML;
                // --- ADIÇÃO v5.01.2: Chama renderPagination ---
                renderPagination(data.pagination);
            });
    };

    window.reactivateAccount = (contaId) => {
        if (confirm('Tem certeza que deseja reativar esta conta?')) {
            fetch(`/admin/api/accounts/${contaId}/reactivate`, { method: 'POST' })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    fetchAndRenderAccounts(); // Atualiza a lista
                } else {
                    alert('Erro ao reativar conta: ' + (data.error || 'Erro desconhecido'));
                }
            });
        }
    };

    // --- ADIÇÃO v5.01.2: Nova função para aplicar filtros e busca ---
    const applyFiltersAndSearch = () => {
        currentPage = 1;
        fetchAndRenderAccounts();
    };

    activeFilter.addEventListener('click', (e) => {
        e.preventDefault();
        currentStatus = 'active';
        activeFilter.classList.add('active');
        inactiveFilter.classList.remove('active');
        // --- ALTERAÇÃO v5.01.2: Chama applyFiltersAndSearch ao invés de fetchAndRenderAccounts ---
        applyFiltersAndSearch();
    });

    inactiveFilter.addEventListener('click', (e) => {
        e.preventDefault();
        currentStatus = 'inactive';
        inactiveFilter.classList.add('active');
        activeFilter.classList.remove('active');
        // --- ALTERAÇÃO v5.01.2: Chama applyFiltersAndSearch ao invés de fetchAndRenderAccounts ---
        applyFiltersAndSearch();
    });

    // --- ADIÇÃO v5.01.2: Event listener para busca ---
    searchInput.addEventListener('keyup', () => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(applyFiltersAndSearch, 500);
    });

    fetchAndRenderAccounts(); // Carga inicial
});