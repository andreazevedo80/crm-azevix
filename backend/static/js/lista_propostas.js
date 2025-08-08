document.addEventListener("DOMContentLoaded", function() {
    const tableBody = document.getElementById('propostas-table-body');
    const paginationControls = document.getElementById('pagination-controls');

    const loadingSpinner = `<tr><td colspan="7" class="text-center py-5"><div class="spinner-border text-azevix" role="status"></div></td></tr>`;

    const formatCurrency = (value) => {
        return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);
    };

    const fetchAndRenderPropostas = (page = 1) => {
        tableBody.innerHTML = loadingSpinner;
        
        const url = `/api/propostas?page=${page}`;

        fetch(url)
            .then(response => response.json())
            .then(data => {
                tableBody.innerHTML = '';
                if (data.success && data.propostas.length > 0) {
                    data.propostas.forEach(prop => {
                        const row = document.createElement('tr');
                        row.style.cursor = 'pointer';
                        row.onclick = () => { window.location.href = `/propostas/${prop.id}` };
                        
                        row.innerHTML = `
                            <td>${prop.numero_proposta}</td>
                            <td>${prop.conta_nome}</td>
                            <td>${prop.lead_titulo}</td>
                            <td>${formatCurrency(prop.valor_total)}</td>
                            <td><span class="badge bg-secondary">${prop.status}</span></td>
                            <td>${prop.criador_nome}</td>
                            <td>${prop.data_criacao}</td>
                        `;
                        tableBody.appendChild(row);
                    });
                } else {
                    tableBody.innerHTML = '<tr><td colspan="7" class="text-center">Nenhuma proposta encontrada.</td></tr>';
                }
                renderPagination(data.pagination);
            });
    };

    const renderPagination = (pagination) => {
        // (Lógica de paginação, similar à de lista_contas.js)
        // ...
    };

    fetchAndRenderPropostas();
});