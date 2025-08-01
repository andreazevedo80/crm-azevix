document.addEventListener('DOMContentLoaded', function() {
    // --- ELEMENTOS DO FORMULÁRIO ---
    const form = document.getElementById('status-form');
    const formTitle = document.getElementById('form-title');
    const statusIdInput = document.getElementById('status-id');
    const statusNomeInput = document.getElementById('status-nome');
    const statusDescricaoInput = document.getElementById('status-descricao');
    const statusEstagioSelect = document.getElementById('status-estagio');
    const statusIsLossCheck = document.getElementById('status-is-loss');
    const statusIsInitialCheck = document.getElementById('status-is-initial');
    const cancelBtn = document.getElementById('cancel-btn');
    const tableBody = document.getElementById('statuses-table-body');
    const transitionsContainer = document.getElementById('transitions-container');

    let currentStatuses = [];
    let estagiosOptions = [];

    // --- ADIÇÃO v9.1: Função para renderizar os checkboxes de transição ---
    const renderTransitions = (selectedTransitionIds = []) => {
        transitionsContainer.innerHTML = '';
        currentStatuses.forEach(status => {
            // Não pode fazer transição para si mesmo
            if (status.id === parseInt(statusIdInput.value)) return;

            const isChecked = selectedTransitionIds.includes(status.id);
            const col = document.createElement('div');
            col.className = 'col-md-4';
            col.innerHTML = `
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" value="${status.id}" id="trans-${status.id}" ${isChecked ? 'checked' : ''}>
                    <label class="form-check-label" for="trans-${status.id}">
                        ${status.nome}
                    </label>
                </div>
            `;
            transitionsContainer.appendChild(col);
        });
    };

    // --- FUNÇÕES DE RENDERIZAÇÃO E API ---
    const renderTable = () => {
        tableBody.innerHTML = '';
        currentStatuses.forEach(status => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${status.nome}</td>
                <td>${status.descricao || ''}</td>
                <td><span class="badge bg-secondary">${status.estagio_alvo || 'N/A'}</span></td>
                <td class="text-center">${status.is_loss_status ? '<i class="fas fa-check text-success"></i>' : ''}</td>
                <td class="text-center">${status.is_initial_status ? '<i class="fas fa-check text-success"></i>' : ''}</td>
                <td>
                    <span class="badge bg-${status.is_active ? 'success' : 'danger'}">
                        ${status.is_active ? 'Ativo' : 'Inativo'}
                    </span>
                </td>
                <td>
                    <button class="btn btn-sm btn-outline-secondary" onclick="handleEdit(${status.id})"><i class="fas fa-pencil-alt"></i></button>
                    <button class="btn btn-sm btn-outline-${status.is_active ? 'danger' : 'success'}" onclick="handleToggleActive(${status.id}, ${!status.is_active})">
                        <i class="fas ${status.is_active ? 'fa-toggle-off' : 'fa-toggle-on'}"></i>
                    </button>
                </td>
            `;
            tableBody.appendChild(row);
        });
    };

    const fetchStatuses = () => {
        fetch('/admin/api/statuses')
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    currentStatuses = data.statuses;
                    renderTable();
                }
            });
    };

    const fetchConfigData = async () => {
        try {
            const response = await fetch('/api/leads/config'); // Reutiliza a API de config dos leads
            const data = await response.json();
            if (data.success) {
                estagiosOptions = data.estagios;
                populateSelect(statusEstagioSelect, estagiosOptions);
            }
        } catch (error) { console.error("Erro ao carregar configurações:", error); }
    };
    
    const populateSelect = (selectElement, options) => {
        selectElement.innerHTML = '<option value="">Selecione...</option>';
        options.forEach(opt => selectElement.add(new Option(opt, opt)));
    };

    const resetForm = () => {
        form.reset();
        statusIdInput.value = '';
        formTitle.textContent = 'Adicionar Novo Status';
        cancelBtn.style.display = 'none';
        transitionsContainer.innerHTML = '<p class="text-muted">Salve o status primeiro para definir as transições.</p>';
    };

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const id = statusIdInput.value;
        
        // --- ADIÇÃO v9.1: Coleta os IDs das transições selecionadas ---
        const selectedTransitions = Array.from(transitionsContainer.querySelectorAll('input[type="checkbox"]:checked')).map(cb => parseInt(cb.value));

        const data = {
            nome: statusNomeInput.value,
            descricao: statusDescricaoInput.value,
            estagio_alvo: statusEstagioSelect.value,
            is_loss_status: statusIsLossCheck.checked,
            is_initial_status: statusIsInitialCheck.checked,
            transition_ids: selectedTransitions // Envia a lista para a API
        };
        
        const url = id ? `/admin/api/statuses/${id}` : '/admin/api/statuses';
        const method = id ? 'PUT' : 'POST';

        fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
        .then(res => res.json())
        .then(result => {
            if(result.success) {
                fetchStatuses();
                resetForm();
            } else {
                alert(`Erro: ${result.error}`);
            }
        });
    });

    window.handleEdit = (id) => {
        const status = currentStatuses.find(s => s.id === id);
        if (status) {
            formTitle.textContent = 'Editar Status';
            statusIdInput.value = status.id;
            statusNomeInput.value = status.nome;
            statusDescricaoInput.value = status.descricao;
            statusEstagioSelect.value = status.estagio_alvo;
            statusIsLossCheck.checked = status.is_loss_status;
            statusIsInitialCheck.checked = status.is_initial_status;
            cancelBtn.style.display = 'inline-block';
            
            // --- ADIÇÃO v9.1: Renderiza os checkboxes de transição ---
            renderTransitions(status.proximos_status_ids);

            window.scrollTo(0, 0);
        }
    };
    
    window.handleToggleActive = (id, newStatus) => {
        const status = currentStatuses.find(s => s.id === id);
        // Precisamos enviar todos os dados para a API PUT, mesmo que só mudemos um
        const updatedData = { ...status, is_active: newStatus };

        fetch(`/admin/api/statuses/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updatedData)
        })
        .then(res => res.json())
        .then(data => {
            if(data.success) {
                fetchStatuses();
            }
        });
    };

    cancelBtn.addEventListener('click', resetForm);

    const init = async () => {
        await fetchConfigData();
        fetchStatuses();
    };

    init();
});