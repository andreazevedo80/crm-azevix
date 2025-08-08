document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('catalog-form');
    const formTitle = document.getElementById('form-title');
    const itemIdInput = document.getElementById('item-id');
    const nomeInput = document.getElementById('item-nome');
    const tipoSelect = document.getElementById('item-tipo');
    const cobrancaSelect = document.getElementById('item-cobranca');
    const precoInput = document.getElementById('item-preco');
    const sobConsultaCheck = document.getElementById('item-sob-consulta');
    const descricaoInput = document.getElementById('item-descricao');
    const catmatInput = document.getElementById('item-catmat');
    const palavrasChaveInput = document.getElementById('item-palavras-chave');
    const cancelBtn = document.getElementById('cancel-btn');
    const tableBody = document.getElementById('catalog-table-body');
    const activitiesSection = document.getElementById('activities-section');
    const activitiesContainer = document.getElementById('activities-container');

    let currentItems = [];
    let availableActivities = [];

    const renderTable = () => {
        tableBody.innerHTML = '';
        currentItems.forEach(item => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${item.nome}</td>
                <td>${item.tipo_item}</td>
                <td>${item.tipo_cobranca}</td>
                <td>${item.preco_sob_consulta ? 'Sob Consulta' : `R$ ${parseFloat(item.preco_base).toFixed(2)}`}</td>
                <td><span class="badge bg-${item.is_active ? 'success' : 'danger'}">${item.is_active ? 'Ativo' : 'Inativo'}</span></td>
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
                    availableActivities = data.activities;
                    renderTable();
                }
            });
    };
    
    const resetForm = () => {
        form.reset();
        itemIdInput.value = '';
        formTitle.textContent = 'Adicionar Novo Item';
        cancelBtn.style.display = 'none';
        precoInput.disabled = false;
    };

    const renderActivitiesCheckboxes = (selectedActivityIds = []) => {
        activitiesContainer.innerHTML = '';
        availableActivities.forEach(activity => {
            const isChecked = selectedActivityIds.includes(activity.id);
            const col = document.createElement('div');
            col.className = 'col-md-4';
            col.innerHTML = `
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" value="${activity.id}" id="act-${activity.id}" ${isChecked ? 'checked' : ''}>
                    <label class="form-check-label" for="act-${activity.id}">${activity.nome}</label>
                </div>
            `;
            activitiesContainer.appendChild(col);
        });
    };

    sobConsultaCheck.addEventListener('change', () => {
        precoInput.disabled = sobConsultaCheck.checked;
        if (sobConsultaCheck.checked) {
            precoInput.value = '';
        }
    });

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const id = itemIdInput.value;
        const selectedActivities = Array.from(activitiesContainer.querySelectorAll('input[type="checkbox"]:checked')).map(cb => parseInt(cb.value));
        
        const data = {
            nome: nomeInput.value,
            tipo_item: tipoSelect.value,
            tipo_cobranca: cobrancaSelect.value,
            preco_base: precoInput.value,
            preco_sob_consulta: sobConsultaCheck.checked,
            descricao: descricaoInput.value,
            catmat_catser: catmatInput.value,
            palavras_chave_licitacao: palavrasChaveInput.value,
            activity_ids: selectedActivities
        };
        
        const url = id ? `/admin/api/catalog/${id}` : '/admin/api/catalog';
        const method = id ? 'PUT' : 'POST';

        fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
        .then(res => res.json())
        .then(result => {
            if(result.success) {
                fetchItems();
                resetForm();
            } else {
                alert(`Erro: ${result.error}`);
            }
        });
    });

    window.handleEdit = (id) => {
        const item = currentItems.find(i => i.id === id);
        if (item) {
            formTitle.textContent = 'Editar Item';
            itemIdInput.value = item.id;
            nomeInput.value = item.nome;
            tipoSelect.value = item.tipo_item;
            cobrancaSelect.value = item.tipo_cobranca;
            precoInput.value = item.preco_base;
            sobConsultaCheck.checked = item.preco_sob_consulta;
            descricaoInput.value = item.descricao;
            catmatInput.value = item.catmat_catser;
            palavrasChaveInput.value = item.palavras_chave_licitacao;
            cancelBtn.style.display = 'inline-block';
            precoInput.disabled = item.preco_sob_consulta;

            // Mostra a seção de atividades apenas se for um serviço
            if (item.tipo_item === 'Serviço Pontual' || item.tipo_item === 'Consultoria') {
                activitiesSection.style.display = 'block';
                renderActivitiesCheckboxes(item.atividade_ids);
            } else {
                activitiesSection.style.display = 'none';
            }

            window.scrollTo(0, 0);
        }
    };
    
    window.handleToggleActive = (id, newStatus) => {
        const item = currentItems.find(i => i.id === id);
        const updatedData = { ...item, is_active: newStatus };

        fetch(`/admin/api/catalog/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updatedData)
        })
        .then(res => res.json())
        .then(data => {
            if(data.success) {
                fetchItems();
            }
        });
    };

    cancelBtn.addEventListener('click', resetForm);
    fetchItems();
});