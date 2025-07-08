document.addEventListener("DOMContentLoaded", function() {
    const elements = {
        displayArea: document.getElementById('leads-display-area'),
        searchInput: document.getElementById('search-filter'),
        statusFilter: document.getElementById('status-filter'),
        segmentFilter: document.getElementById('segment-filter'),
        checkModalInput: document.getElementById('check-company-name'),
        checkResultsContainer: document.getElementById('check-results-container'),
        proceedButton: document.getElementById('proceed-to-register-btn'),
        checkModalInstance: document.getElementById('checkLeadModal')
    };

    const loadingSpinner = `<div class="text-center py-5"><div class="spinner-border text-azevix" role="status"></div></div>`;

    const populateFilters = () => {
        fetch('/api/config')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    data.status_leads.forEach(status => elements.statusFilter.add(new Option(status, status)));
                    data.segmentos.forEach(seg => elements.segmentFilter.add(new Option(seg, seg)));
                }
            });
    };

    const fetchAndRenderLeads = () => {
        elements.displayArea.innerHTML = loadingSpinner;
        const params = new URLSearchParams({
            search: elements.searchInput.value,
            status: elements.statusFilter.value,
            segmento: elements.segmentFilter.value
        });

        fetch(`/api/leads?${params.toString()}`)
            .then(response => response.json())
            .then(data => {
                let tableContent = '';
                if (data.success && data.leads.length > 0) {
                    const rows = data.leads.map(lead => `
                        <tr>
                            <td>${lead.nome_completo}</td>
                            <td>${lead.nome_conta}</td>
                            <td>${lead.email || '-'}</td>
                            <td>${lead.telefone_celular || '-'}</td>
                            <td><span class="badge bg-primary">${lead.status_lead}</span></td>
                            <td>${lead.owner_name}</td>
                            <td><button class="btn btn-sm btn-outline-secondary" disabled>Editar</button></td>
                        </tr>`).join('');
                    tableContent = `<div class="table-responsive"><table class="table table-hover"><thead><tr><th>Contato</th><th>Empresa</th><th>Email</th><th>Telefone</th><th>Status</th><th>Responsável</th><th>Ações</th></tr></thead><tbody>${rows}</tbody></table></div>`;
                } else {
                    tableContent = `<p class="text-center py-4">Nenhum lead encontrado para você.</p>`;
                }
                elements.displayArea.innerHTML = tableContent;
            });
    };

    const checkDuplicates = () => {
        const term = elements.checkModalInput.value;
        elements.proceedButton.style.display = 'none';
        if (term.length < 3) {
            elements.checkResultsContainer.innerHTML = `<p class="text-muted">Digite pelo menos 3 caracteres.</p>`;
            return;
        }
        elements.checkResultsContainer.innerHTML = `<div class="spinner-border spinner-border-sm" role="status"></div>`;
        fetch(`/api/leads/check_duplicates?term=${encodeURIComponent(term)}`)
            .then(response => response.json())
            .then(data => {
                if (data.success && data.duplicates.length > 0) {
                    const duplicatesList = data.duplicates.map(lead => `<li class="list-group-item"><strong>${lead.nome_conta}</strong> (Responsável: ${lead.owner_name})</li>`).join('');
                    elements.checkResultsContainer.innerHTML = `<p class="text-danger"><strong>Atenção!</strong> Empresas similares encontradas:</p><ul class="list-group">${duplicatesList}</ul>`;
                } else {
                    elements.checkResultsContainer.innerHTML = `<p class="text-success">Nenhuma empresa encontrada. Pode prosseguir.</p>`;
                    elements.proceedButton.style.display = 'inline-block';
                }
            });
    };

    let searchTimeout;
    elements.searchInput.addEventListener('keyup', () => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(fetchAndRenderLeads, 500);
    });
    elements.statusFilter.addEventListener('change', fetchAndRenderLeads);
    elements.segmentFilter.addEventListener('change', fetchAndRenderLeads);

    let checkTimeout;
    elements.checkModalInput.addEventListener('keyup', () => {
        clearTimeout(checkTimeout);
        checkTimeout = setTimeout(checkDuplicates, 500);
    });
    elements.checkModalInstance.addEventListener('hidden.bs.modal', () => {
        elements.checkModalInput.value = '';
        elements.checkResultsContainer.innerHTML = '';
        elements.proceedButton.style.display = 'none';
    });

    populateFilters();
    fetchAndRenderLeads();
});