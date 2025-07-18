document.addEventListener("DOMContentLoaded", function() {
    // --- ELEMENTOS DA PÁGINA ---
    const displayArea = document.getElementById('contas-display-area');
    const searchInput = document.getElementById('search-filter');
    const segmentFilter = document.getElementById('segment-filter');
    const ownerFilter = document.getElementById('owner-filter');
    const paginationContainer = document.getElementById('pagination-container');
    const checkModalInput = document.getElementById('check-conta-input');
    const checkResultsContainer = document.getElementById('check-results-container');
    const proceedButton = document.getElementById('proceed-to-register-btn');
    const checkModalEl = document.getElementById('checkContaModal');

    const loadingSpinner = `<div class="text-center py-5"><div class="spinner-border text-azevix" role="status"></div></div>`;
    
    // --- ADIÇÃO v4.01: Estado da Paginação ---
    let currentPage = 1;

    const populateFilters = async () => {
        try {
            const response = await fetch('/api/contas/config');
            const data = await response.json();
            if (data.success && data.segmentos) {
                data.segmentos.forEach(seg => segmentFilter.add(new Option(seg, seg)));
            }
        } catch (error) { console.error("Erro ao carregar segmentos:", error); }

        // Popula o filtro de vendedores apenas se o elemento existir (ou seja, se o usuário for admin e gerente)
        if (CAN_FILTER_BY_OWNER && ownerFilter) {
            try {
                const response = await fetch('/api/admin/form_data');
                const data = await response.json();
                if (data.success && data.vendedores) {
                    data.vendedores.forEach(v => ownerFilter.add(new Option(v.name, v.id)));
                }
            } catch (error) { console.error("Erro ao carregar vendedores:", error); }
        }
    };

    // --- ADIÇÃO v4.01: Função para renderizar a paginação ---
    const renderPagination = (pagination) => {
        paginationContainer.innerHTML = '';
        if (pagination.pages <= 1) return;

        let paginationHTML = '<ul class="pagination">';
        
        // Botão Anterior
        paginationHTML += `<li class="page-item ${!pagination.has_prev ? 'disabled' : ''}"><a class="page-link" href="#" data-page="${pagination.page - 1}">Anterior</a></li>`;

        // Botões de Página
        for (let i = 1; i <= pagination.pages; i++) {
            paginationHTML += `<li class="page-item ${i === pagination.page ? 'active' : ''}"><a class="page-link" href="#" data-page="${i}">${i}</a></li>`;
        }

        // Botão Próximo
        paginationHTML += `<li class="page-item ${!pagination.has_next ? 'disabled' : ''}"><a class="page-link" href="#" data-page="${pagination.page + 1}">Próximo</a></li>`;

        paginationHTML += '</ul>';
        paginationContainer.innerHTML = paginationHTML;

        // Adiciona listeners aos novos botões de página
        paginationContainer.querySelectorAll('.page-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const newPage = e.target.dataset.page;
                if (newPage && currentPage !== newPage) {
                    currentPage = parseInt(newPage);
                    renderContas();
                }
            });
        });
    };

    const renderContas = () => {
        displayArea.innerHTML = loadingSpinner;
        const params = new URLSearchParams({
            search: searchInput.value,
            segmento: segmentFilter.value,
            page: currentPage // Envia a página atual
        });

        if (CAN_FILTER_BY_OWNER && ownerFilter && ownerFilter.value) {
            params.append('owner_id', ownerFilter.value);
        }

        fetch(`/api/contas?${params.toString()}`)
            .then(res => res.json())
            .then(data => {
                let tableContent = '';
                if (data.success && data.contas.length > 0) {
                    const rows = data.contas.map(conta => `
                        <tr>
                            <td><a href="/contas/${conta.id}">${conta.nome_fantasia}</a></td>
                            <td>${conta.cnpj || '-'}</td>
                            <td><span class="badge bg-secondary">${conta.tipo_conta}</span></td>
                            <td>${conta.segmento || '-'}</td>
                            <td>${conta.owner_name}</td>
                            <td><a href="/contas/${conta.id}" class="btn btn-sm btn-outline-primary">Detalhes</a></td>
                        </tr>`).join('');
                    tableContent = `<div class="table-responsive"><table class="table table-hover"><thead><tr><th>Nome Fantasia</th><th>CNPJ</th><th>Tipo</th><th>Segmento</th><th>Responsável</th></tr></thead><tbody>${rows}</tbody></table></div>`;
                } else {
                    // CORRIGIDO: O link agora abre o modal de busca, não vai direto para o cadastro.
                    tableContent = `<p class="text-center py-4">Nenhuma conta encontrada. <a href="#" data-bs-toggle="modal" data-bs-target="#checkContaModal">Cadastre a primeira!</a></p>`;
                }
                displayArea.innerHTML = tableContent;
                // --- ALTERAÇÃO v4.01: Renderiza a paginação ---
                renderPagination(data.pagination);
            });
    };

    const checkDuplicates = () => {
        const term = checkModalInput.value;
        proceedButton.style.display = 'none';

        if (term.length < 3) {
            checkResultsContainer.innerHTML = `<p class="text-muted">Digite pelo menos 3 caracteres.</p>`;
            return;
        }

        checkResultsContainer.innerHTML = `<div class="spinner-border spinner-border-sm" role="status"></div> Buscando...`;
        fetch(`/api/contas/search?term=${encodeURIComponent(term)}`)
            .then(res => res.json())
            .then(data => {
                if (data.success && data.contas.length > 0) {
                    let resultsHtml = '<p class="text-danger"><strong>Atenção!</strong> Contas similares encontradas:</p><ul class="list-group">';
                    data.contas.forEach(conta => {
                        resultsHtml += `<li class="list-group-item"><strong>${conta.nome_fantasia}</strong> (CNPJ: ${conta.cnpj || 'N/A'}) - Responsável: <strong>${conta.owner_name}</strong></li>`;
                    });
                    resultsHtml += '</ul>';
                    checkResultsContainer.innerHTML = resultsHtml;
                } else {
                    checkResultsContainer.innerHTML = `<p class="text-success">Nenhuma conta encontrada. Pode prosseguir.</p>`;
                    proceedButton.style.display = 'inline-block';
                }
            });
    };

    // --- ALTERAÇÃO v4.01: Reseta a página para 1 ao aplicar filtros ---
    const applyFilters = () => {
        currentPage = 1;
        renderContas();
    };

    // --- EVENT LISTENERS ---
    
    // Filtros da página principal
    let searchTimeout;
    searchInput.addEventListener('keyup', () => { clearTimeout(searchTimeout); searchTimeout = setTimeout(applyFilters, 500); });
    segmentFilter.addEventListener('change', applyFilters);
    if(ownerFilter) { ownerFilter.addEventListener('change', applyFilters); }
    
    // Modal de verificação
    checkModalEl.addEventListener('hidden.bs.modal', function () {
        checkModalInput.value = '';
        checkResultsContainer.innerHTML = '';
        proceedButton.style.display = 'none';
    });
    
    let checkTimeout;
    checkModalInput.addEventListener('keyup', () => {
        clearTimeout(checkTimeout);
        checkTimeout = setTimeout(checkDuplicates, 500);
    });

    // --- CARGA INICIAL ---
    const initPage = async () => {
        await populateFilters();
        renderContas();
    };
    initPage();
});