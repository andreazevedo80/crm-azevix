document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('catalog-form');
    const formTitle = document.getElementById('form-title');
    const itemIdInput = document.getElementById('item-id');
    // ... (outros campos do formulário a serem adicionados)
    const cancelBtn = document.getElementById('cancel-btn');
    const tableBody = document.getElementById('catalog-table-body');

    let currentItems = [];

    const renderTable = () => {
        tableBody.innerHTML = '';
        currentItems.forEach(item => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${item.nome}</td>
                <td>${item.tipo_item}</td>
                <td>${item.tipo_cobranca}</td>
                <td>${item.preco_sob_consulta ? 'Sob Consulta' : `R$ ${item.preco_base}`}</td>
                <td>
                    <span class="badge bg-${item.is_active ? 'success' : 'danger'}">
                        ${item.is_active ? 'Ativo' : 'Inativo'}
                    </span>
                </td>
                <td>
                    <button class="btn btn-sm btn-outline-secondary" onclick="handleEdit(${item.id})"><i class="fas fa-pencil-alt"></i></button>
                    <button class="btn btn-sm btn-outline-${item.is_active ? 'danger' : 'success'}" onclick="handleToggleActive(${item.id}, ${!item.is_active})">
                        <i class="fas ${item.is_active ? 'fa-toggle-off' : 'fa-toggle-on'}"></i>
                    </button>
                </td>
            `;
            tableBody.appendChild(row);
        });
    };

    const fetchItems = () => {
        fetch('/admin/api/catalog')
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    currentItems = data.items;
                    renderTable();
                }
            });
    };

    // As funções de 'submit', 'handleEdit' e 'handleToggleActive' serão semelhantes
    // às que implementamos para Status, Segmentos, etc.
    
    fetchItems();
});