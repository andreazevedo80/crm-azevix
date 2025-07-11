document.addEventListener("DOMContentLoaded", function() {
    // --- Referências aos elementos da página ---
    const formEditConta = document.getElementById('form-edit-conta');
    const btnEditConta = document.getElementById('btn-edit-conta');
    const btnCancelEdit = document.getElementById('btn-cancel-edit');
    const editButtons = document.getElementById('edit-buttons');
    const adminFields = document.getElementById('admin-fields');
    const listaContatos = document.getElementById('lista-contatos');
    const listaLeads = document.getElementById('lista-leads');
    const formNovoContato = document.getElementById('form-novo-contato');

    let originalContaData = {};

    const populateSelect = (selectElement, options, selectedValue) => {
        selectElement.innerHTML = '';
        if (selectElement.id === 'edit-matriz' || selectElement.id === 'edit-segmento') {
            selectElement.add(new Option('Selecione...', ''));
        }
        options.forEach(opt => {
            const option = new Option(opt.name || opt, opt.id || opt);
            selectElement.add(option);
        });
        selectElement.value = selectedValue || '';
    };

    const renderInfoForm = (conta) => {
        document.getElementById('edit-nome-fantasia').value = conta.nome_fantasia || '';
        document.getElementById('edit-razao-social').value = conta.razao_social || '';
        document.getElementById('edit-cnpj').value = conta.cnpj || '';
        document.getElementById('edit-tipo_conta').value = conta.tipo_conta || 'Privada';
        document.getElementById('edit-segmento').value = conta.segmento || '';
        if (CURRENT_USER_ROLE === 'admin') {
            document.getElementById('edit-owner').value = conta.owner_id || '';
            document.getElementById('edit-matriz').value = conta.matriz_id || '';
        }
    };

    const renderContatos = (contatos) => {
        listaContatos.innerHTML = '';
        if (contatos && contatos.length > 0) {
            contatos.forEach(c => { listaContatos.innerHTML += `<li class="list-group-item"><strong>${c.nome}</strong> (${c.cargo || 'N/A'})<br><small class="text-muted">${c.email || ''} | ${c.telefone || ''}</small></li>`; });
        } else {
            listaContatos.innerHTML = '<li class="list-group-item text-center">Nenhum contato cadastrado.</li>';
        }
    };

    const renderLeads = (leads) => {
        listaLeads.innerHTML = '';
        if (leads && leads.length > 0) {
            leads.forEach(l => { listaLeads.innerHTML += `<tr><td>${l.titulo}</td><td><span class="badge bg-info">${l.status_lead}</span></td><td>${l.valor_estimado}</td><td>${l.contato_principal_nome}</td><td><a href="#" class="btn btn-sm btn-outline-secondary disabled">Ver</a></td></tr>`; });
        } else {
            listaLeads.innerHTML = '<tr><td colspan="5" class="text-center">Nenhuma oportunidade encontrada.</td></tr>';
        }
    };

    const populateDropdowns = async () => {
        try {
            const configResponse = await fetch('/api/contas/config');
            const configData = await configResponse.json();
            if (configData.success) {
                populateSelect(document.getElementById('edit-segmento'), configData.segmentos);
            }

            if (CURRENT_USER_ROLE === 'admin') {
                const adminResponse = await fetch('/api/admin/form_data');
                const adminData = await adminResponse.json();
                if (adminData.success) {
                    populateSelect(document.getElementById('edit-owner'), adminData.vendedores);
                    populateSelect(document.getElementById('edit-matriz'), adminData.contas);
                }
            }
        } catch (error) { console.error('Erro ao popular dropdowns:', error); }
    };
    
    const fetchDetalhesConta = async () => {
        if (typeof CONTA_ID === 'undefined') return;
        try {
            const response = await fetch(`/api/contas/${CONTA_ID}/details`);
            const data = await response.json();
            if (data.success) {
                originalContaData = data.conta;
                renderInfoForm(data.conta);
                renderContatos(data.contatos);
                renderLeads(data.leads);
                // Repopula os selects com os valores corretos após ter os dados
                populateSelect(document.getElementById('edit-segmento'), SEGMENTOS, originalContaData.segmento);
                if (CURRENT_USER_ROLE === 'admin') {
                    // Aqui você pode recarregar os dados de admin se necessário
                }
            }
        } catch (error) { console.error('Erro ao buscar detalhes da conta:', error); }
    };

    const toggleEditMode = (isEditing) => {
        const fields = formEditConta.querySelectorAll('input, select');
        fields.forEach(field => field.disabled = !isEditing);
        editButtons.style.display = isEditing ? 'block' : 'none';
        btnEditConta.style.display = isEditing ? 'none' : 'block';
        if (CURRENT_USER_ROLE === 'admin' && adminFields) {
            adminFields.style.display = isEditing ? 'block' : 'none';
        }
    };

    btnEditConta.addEventListener('click', () => toggleEditMode(true));
    btnCancelEdit.addEventListener('click', () => {
        renderInfoForm(originalContaData);
        toggleEditMode(false);
    });

    formEditConta.addEventListener('submit', async (e) => {
        e.preventDefault();
        const updatedData = {
            nome_fantasia: document.getElementById('edit-nome-fantasia').value,
            razao_social: document.getElementById('edit-razao-social').value,
            cnpj: document.getElementById('edit-cnpj').value,
            tipo_conta: document.getElementById('edit-tipo_conta').value,
            segmento: document.getElementById('edit-segmento').value,
        };
        if (CURRENT_USER_ROLE === 'admin') {
            updatedData.owner_id = document.getElementById('edit-owner').value;
            updatedData.matriz_id = document.getElementById('edit-matriz').value;
        }

        const response = await fetch(`/api/contas/${CONTA_ID}`, {
            method: 'PUT', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updatedData)
        });
        const result = await response.json();
        if (result.success) {
            toggleEditMode(false);
            document.querySelector('h1.text-azevix').innerHTML = `<i class="fas fa-building me-2"></i>${updatedData.nome_fantasia}`;
            await fetchDetalhesConta();
            alert('Conta atualizada com sucesso!');
        } else { alert(`Falha ao atualizar: ${result.error || 'Erro desconhecido'}`); }
    });

    formNovoContato.addEventListener('submit', async function(e) {
        e.preventDefault();
        const nome = document.getElementById('novo-contato-nome').value;
        if (!nome) { alert('O nome do contato é obrigatório.'); return; }
        const novoContatoData = { nome, email: document.getElementById('novo-contato-email').value, telefone: document.getElementById('novo-contato-telefone').value, cargo: document.getElementById('novo-contato-cargo').value };
        const response = await fetch(`/api/contas/${CONTA_ID}/contatos`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(novoContatoData) });
        const result = await response.json();
        if (result.success) {
            formNovoContato.reset();
            await fetchDetalhesConta();
        } else { alert('Erro ao adicionar contato: ' + result.error); }
    });

    const initPage = async () => {
        await populateDropdowns();
        await fetchDetalhesConta();
    };
    initPage();
});