document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('package-form');
    const formTitle = document.getElementById('form-title-package');
    const packageIdInput = document.getElementById('package-id');
    const nomeInput = document.getElementById('package-nome');
    const descricaoInput = document.getElementById('package-descricao');
    const precoInput = document.getElementById('package-preco');
    const itemsSelect = document.getElementById('package-items');
    const cancelBtn = document.getElementById('cancel-btn-package');
    const tableBody = document.getElementById('packages-table-body');

    let currentPackages = [];
    let catalogItems = [];

    const renderTable = () => {
        tableBody.innerHTML = '';
        currentPackages.forEach(pkg => {
            const row = document.createElement('tr');
            const itemCount = pkg.item_ids ? pkg.item_ids.length : 0;
            row.innerHTML = `
                <td><strong>${pkg.nome}</strong><br><small class="text-muted">${pkg.descricao || ''}</small></td>
                <td>R$ ${parseFloat(pkg.preco_total).toFixed(2)}</td>
                <td><span class="badge bg-secondary">${itemCount}</span></td>
                <td><span class="badge bg-${pkg.is_active ? 'success' : 'danger'}">${pkg.is_active ? 'Ativo' : 'Inativo'}</span></td>
                <td>
                    <button class="btn btn-sm btn-outline-secondary" onclick="handleEdit(${pkg.id})"><i class="fas fa-pencil-alt"></i></button>
                    <button class="btn btn-sm btn-outline-${pkg.is_active ? 'danger' : 'success'}" onclick="handleToggleActive(${pkg.id}, ${!pkg.is_active})"><i class="fas ${pkg.is_active ? 'fa-toggle-off' : 'fa-toggle-on'}"></i></button>
                </td>
            `;
            tableBody.appendChild(row);
        });
    };
    
    const populateItemsSelect = () => {
        itemsSelect.innerHTML = '';
        catalogItems.forEach(item => {
            itemsSelect.add(new Option(item.nome, item.id));
        });
    };

    const fetchPackages = () => {
        fetch('/admin/api/packages')
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    currentPackages = data.packages;
                    catalogItems = data.catalog_items;
                    renderTable();
                    populateItemsSelect();
                }
            });
    };
    
    const resetForm = () => {
        form.reset();
        packageIdInput.value = '';
        formTitle.textContent = 'Adicionar Novo Pacote';
        cancelBtn.style.display = 'none';
        // Limpa a seleção do select múltiplo
        Array.from(itemsSelect.options).forEach(opt => opt.selected = false);
    };

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const id = packageIdInput.value;
        const selectedItems = Array.from(itemsSelect.selectedOptions).map(opt => parseInt(opt.value));
        const data = {
            nome: nomeInput.value,
            descricao: descricaoInput.value,
            preco_total: precoInput.value,
            item_ids: selectedItems
        };
        
        const url = id ? `/admin/api/packages/${id}` : '/admin/api/packages';
        const method = id ? 'PUT' : 'POST';

        fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
        .then(res => res.json())
        .then(result => {
            if(result.success) {
                fetchPackages();
                resetForm();
            } else {
                alert(`Erro: ${result.error}`);
            }
        });
    });

    window.handleEdit = (id) => {
        const pkg = currentPackages.find(p => p.id === id);
        if (pkg) {
            formTitle.textContent = 'Editar Pacote';
            packageIdInput.value = pkg.id;
            nomeInput.value = pkg.nome;
            descricaoInput.value = pkg.descricao;
            precoInput.value = pkg.preco_total;
            
            // Pré-seleciona os itens no select múltiplo
            Array.from(itemsSelect.options).forEach(opt => {
                opt.selected = pkg.item_ids.includes(parseInt(opt.value));
            });

            cancelBtn.style.display = 'inline-block';
            window.scrollTo(0, 0);
        }
    };
    
    window.handleToggleActive = (id, newStatus) => {
        const pkg = currentPackages.find(p => p.id === id);
        fetch(`/admin/api/packages/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ...pkg, item_ids: pkg.item_ids, is_active: newStatus })
        })
        .then(res => res.json())
        .then(data => {
            if(data.success) {
                fetchPackages();
            }
        });
    };

    cancelBtn.addEventListener('click', resetForm);
    fetchPackages();
});