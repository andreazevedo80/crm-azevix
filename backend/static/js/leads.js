document.addEventListener("DOMContentLoaded", function() {
    const loadingDiv = document.getElementById('loading');
    const tableContainer = document.getElementById('leads-table-container');
    const leadsListBody = document.getElementById('leads-list');
    const searchInput = document.getElementById('search-filter');

    const fetchLeads = () => {
        loadingDiv.style.display = 'block';
        tableContainer.style.display = 'none';

        const searchTerm = searchInput.value;
        const url = `/api/leads?search=${encodeURIComponent(searchTerm)}`;

        fetch(url)
            .then(response => response.json())
            .then(data => {
                leadsListBody.innerHTML = ''; // Limpa a tabela
                if (data.leads && data.leads.length > 0) {
                    data.leads.forEach(lead => {
                        const row = `
                            <tr>
                                <td>${lead.nome_completo}</td>
                                <td>${lead.nome_conta}</td>
                                <td>${lead.email || '-'}</td>
                                <td>${lead.telefone_celular || '-'}</td>
                                <td><span class="badge bg-info">${lead.status_lead}</span></td>
                                <td>
                                    <button class="btn btn-sm btn-outline-primary">Editar</button>
                                </td>
                            </tr>
                        `;
                        leadsListBody.innerHTML += row;
                    });
                } else {
                    leadsListBody.innerHTML = '<tr><td colspan="6" class="text-center">Nenhum lead encontrado.</td></tr>';
                }
            })
            .catch(error => {
                console.error('Erro ao buscar leads:', error);
                leadsListBody.innerHTML = '<tr><td colspan="6" class="text-center text-danger">Erro ao carregar os leads.</td></tr>';
            })
            .finally(() => {
                loadingDiv.style.display = 'none';
                tableContainer.style.display = 'block';
            });
    };

    // Event listener para a busca
    let searchTimeout;
    searchInput.addEventListener('keyup', () => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(fetchLeads, 500); // Espera 500ms após o usuário parar de digitar
    });

    // Carga inicial
    fetchLeads();
});