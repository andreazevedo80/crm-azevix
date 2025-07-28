document.addEventListener('DOMContentLoaded', function() {
    const tableBody = document.getElementById('history-table-body');
    const errorListContainer = document.getElementById('error-list-container');
    const errorModal = new bootstrap.Modal(document.getElementById('errorDetailsModal'));

    const renderHistory = (history) => {
        tableBody.innerHTML = '';
        if (history.length > 0) {
            history.forEach(item => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${item.data_importacao}</td>
                    <td>${item.user_name}</td>
                    <td>${item.nome_arquivo}</td>
                    <td><span class="badge bg-success">${item.sucesso_count}</span></td>
                    <td><span class="badge bg-danger">${item.erro_count}</span></td>
                    <td>
                        ${item.erro_count > 0 ? `<button class="btn btn-sm btn-outline-warning" onclick='showErrors(${JSON.stringify(item.erros)})'>Ver Erros</button>` : ''}
                    </td>
                `;
                tableBody.appendChild(row);
            });
        } else {
            tableBody.innerHTML = '<tr><td colspan="6" class="text-center">Nenhum histórico de importação encontrado.</td></tr>';
        }
    };

    window.showErrors = (errors) => {
        errorListContainer.innerHTML = errors.map(err => `<li class="list-group-item">${err}</li>`).join('');
        errorModal.show();
    };

    fetch('/admin/api/imports')
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                renderHistory(data.history);
            }
        });
});