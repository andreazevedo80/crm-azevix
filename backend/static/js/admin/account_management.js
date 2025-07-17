document.addEventListener("DOMContentLoaded", function() {
    const activeFilter = document.getElementById('filter-active');
    const inactiveFilter = document.getElementById('filter-inactive');
    const container = document.getElementById('accounts-table-container');
    let currentStatus = 'active';

    const loadingSpinner = `<div class="text-center py-5"><div class="spinner-border text-azevix" role="status"></div></div>`;

    const fetchAndRenderAccounts = () => {
        container.innerHTML = loadingSpinner;
        fetch(`/admin/api/accounts?status=${currentStatus}`)
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

    activeFilter.addEventListener('click', (e) => {
        e.preventDefault();
        currentStatus = 'active';
        activeFilter.classList.add('active');
        inactiveFilter.classList.remove('active');
        fetchAndRenderAccounts();
    });

    inactiveFilter.addEventListener('click', (e) => {
        e.preventDefault();
        currentStatus = 'inactive';
        inactiveFilter.classList.add('active');
        activeFilter.classList.remove('active');
        fetchAndRenderAccounts();
    });

    fetchAndRenderAccounts(); // Carga inicial
});