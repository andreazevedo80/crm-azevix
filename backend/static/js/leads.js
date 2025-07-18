document.addEventListener("DOMContentLoaded", function() {
    const container = document.getElementById('leads-table-container');
    const loadingSpinner = `<div class="text-center py-5"><div class="spinner-border text-azevix" role="status"></div></div>`;

    const fetchAndRenderLeads = () => {
        container.innerHTML = loadingSpinner;
        
        // A lógica de busca, filtros e paginação será adicionada aqui
        fetch('/api/leads') 
            .then(res => res.json())
            .then(data => {
                let tableHTML = `
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>Título da Oportunidade</th>
                                <th>Conta</th>
                                <th>Status</th>
                                <th>Responsável</th>
                                <th>Ações</th>
                            </tr>
                        </thead>
                        <tbody>`;
                
                if (data.success && data.leads.length > 0) {
                    // O loop para renderizar as linhas entrará aqui
                } else {
                    tableHTML += '<tr><td colspan="5" class="text-center">Nenhum lead encontrado.</td></tr>';
                }

                tableHTML += '</tbody></table>';
                container.innerHTML = tableHTML;
            });
    };

    fetchAndRenderLeads(); // Carga inicial
});