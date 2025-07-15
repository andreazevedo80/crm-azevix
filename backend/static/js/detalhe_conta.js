document.addEventListener("DOMContentLoaded", function() {
    const formEditConta = document.getElementById('form-edit-conta');
    const btnEditConta = document.getElementById('btn-edit-conta');
    const btnCancelEdit = document.getElementById('btn-cancel-edit');
    const editButtons = document.getElementById('edit-buttons');
    const adminFields = document.getElementById('admin-fields');
    const listaContatos = document.getElementById('lista-contatos');
    const listaLeads = document.getElementById('lista-leads');
    const formNovoContato = document.getElementById('form-novo-contato');
    const hierarchyInfo = document.getElementById('hierarchy-info');
    const hierarchyHr = document.getElementById('hierarchy-hr');
    const matrizSearchInput = document.getElementById('edit-matriz-search');
    const matrizIdInput = document.getElementById('edit-matriz-id');
    const matrizResults = document.getElementById('edit-matriz-results');
    const editContatoModalEl = document.getElementById('editContatoModal');
    const editContatoModal = new bootstrap.Modal(editContatoModalEl);
    const formEditContato = document.getElementById('form-edit-contato');
    const logAuditoriaContainer = document.getElementById('log-auditoria-container');
    const btnDesativarConta = document.getElementById('btn-desativar-conta');
    
    // Estado da aplicação
    let originalContaData = {};

    const populateSelect = (selectElement, options, selectedValue) => {
        selectElement.innerHTML = '';
        if (selectElement.id === 'edit-segmento') selectElement.add(new Option('Selecione...', ''));
        if (selectElement.id === 'edit-matriz') selectElement.add(new Option('Nenhuma', ''));
        
        options.forEach(opt => {
            const text = opt.name || opt.nome_fantasia || opt;
            const value = opt.id || opt;
            selectElement.add(new Option(text, value));
        });
        selectElement.value = selectedValue || '';
    };

    const renderInfoForm = (conta) => {
        document.getElementById('edit-nome-fantasia').value = conta.nome_fantasia || '';
        document.getElementById('edit-razao-social').value = conta.razao_social || '';
        document.getElementById('edit-cnpj').value = conta.cnpj || '';
        document.getElementById('edit-tipo_conta').value = conta.tipo_conta || 'Privada';
        document.getElementById('edit-segmento').value = conta.segmento || '';
        matrizSearchInput.value = conta.matriz_nome || '';
        matrizIdInput.value = conta.matriz_id || '';
        if (IS_ADMIN) {
            document.getElementById('edit-owner').value = conta.owner_id || '';
        }
    };

    const renderContatos = (contatos) => {
        listaContatos.innerHTML = '';
        if (contatos && contatos.length > 0) {
            contatos.forEach(c => {
                // --- ALTERAÇÃO: Adicionados botões de ação para cada contato ---
                listaContatos.innerHTML += `
                    <li class="list-group-item d-flex justify-content-between align-items-center">
                        <div>
                            <strong>${c.nome}</strong> (${c.cargo || 'N/A'})<br>
                            <small class="text-muted">${c.email || ''} | ${c.telefone || ''}</small>
                        </div>
                        <div>
                            <button class="btn btn-sm btn-outline-secondary me-1" onclick="openEditContatoModal(${c.id})"><i class="fas fa-pencil-alt"></i></button>
                            <button class="btn btn-sm btn-outline-danger" onclick="handleDeleteContato(${c.id})"><i class="fas fa-trash"></i></button>
                        </div>
                    </li>`;
            });
        } else {
            listaContatos.innerHTML = '<li class="list-group-item text-center">Nenhum contato cadastrado.</li>';
        }
    };

    const renderLeads = (leads) => {
        listaLeads.innerHTML = '';
        if (leads && leads.length > 0) {
            leads.forEach(l => { listaLeads.innerHTML += `<tr><td>${l.titulo}</td><td><span class="badge bg-info">${l.status_lead}</span></td><td>${l.valor_estimado}</td><td>${l.contato_principal_nome}</td><td><a href="#" class="btn btn-sm btn-outline-secondary disabled">Ver</a></td></tr>`; });
        } else { listaLeads.innerHTML = '<tr><td colspan="5" class="text-center">Nenhuma oportunidade encontrada.</td></tr>'; }
    };
    
    const renderHierarchy = (conta) => {
        let hierarchyHtml = '';
        if (conta.matriz_id && conta.matriz_nome) {
            hierarchyHtml += `<p><strong>Conta Matriz:</strong> <a href="/contas/${conta.matriz_id}">${conta.matriz_nome}</a></p>`;
        }
        if (conta.filiais && conta.filiais.length > 0) {
            const filiaisLinks = conta.filiais.map(f => `<a href="/contas/${f.id}">${f.nome_fantasia}</a>`).join(', ');
            hierarchyHtml += `<p><strong>Filiais:</strong> ${filiaisLinks}</p>`;
        }
        hierarchyInfo.innerHTML = hierarchyHtml;
        hierarchyHr.style.display = hierarchyHtml ? 'block' : 'none';
    };

    // --- ADIÇÃO v4.02: Função para renderizar o log de auditoria ---
    const renderAuditoria = (historico) => {
        if (!logAuditoriaContainer) return; // Só executa se o elemento existir
        
        logAuditoriaContainer.innerHTML = '';
        if (historico && historico.length > 0) {
            let historicoHtml = '<ul class="list-group list-group-flush">';
            historico.forEach(item => {
                historicoHtml += `
                    <li class="list-group-item">
                        <p class="mb-1">
                            <strong>${item.campo}</strong> alterado de 
                            "<em>${item.valor_antigo || 'vazio'}</em>" para 
                            "<strong>${item.valor_novo}</strong>".
                        </p>
                        <small class="text-muted">Por: ${item.usuario} em ${item.data}</small>
                    </li>`;
            });
            historicoHtml += '</ul>';
            logAuditoriaContainer.innerHTML = historicoHtml;
        } else {
            logAuditoriaContainer.innerHTML = '<p class="text-center text-muted">Nenhum histórico de alterações encontrado.</p>';
        }
    };

    const populateDropdownsAndFetchDetails = async () => {
        const configResponse = await fetch('/api/contas/config');
        const configData = await configResponse.json();
        if (configData.success) { populateSelect(document.getElementById('edit-segmento'), configData.segmentos); }

        if (IS_ADMIN) {
            const adminResponse = await fetch('/api/admin/form_data');
            const adminData = await adminResponse.json();
            if (adminData.success) {
                populateSelect(document.getElementById('edit-owner'), adminData.vendedores);
            }
        }
        
        if (typeof CONTA_ID === 'undefined') return;
        const response = await fetch(`/api/contas/${CONTA_ID}/details`);
        const data = await response.json();
        if (data.success) {
            originalContaData = data.conta;
            contatosData = data.contatos;
            renderInfoForm(originalContaData);
            renderContatos(data.contatos);
            renderLeads(data.leads);
            renderHierarchy(data.conta);
            
            // --- ADIÇÃO v4.02: Chama a função para buscar o histórico ---
            if (IS_ADMIN || IS_MANAGER) {
                fetch(`/api/contas/${CONTA_ID}/historico`)
                    .then(res => res.json())
                    .then(histData => {
                        if (histData.success) {
                            renderAuditoria(histData.historico);
                        }
                    });
            }
        }
    };
    // --- ADIÇÃO v4.02: Lógica para o modal de desativação ---
    if (btnDesativarConta) {
        const desativarContaModalEl = document.getElementById('desativarContaModal');
        const desativarContaModal = new bootstrap.Modal(desativarContaModalEl);
        const btnConfirmDesativar = document.getElementById('btn-confirm-desativar');

        btnDesativarConta.addEventListener('click', () => {
            desativarContaModal.show();
        });

        btnConfirmDesativar.addEventListener('click', () => {
            fetch(`/api/contas/${CONTA_ID}`, { method: 'DELETE' })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    // Redireciona para a lista de contas após a desativação
                    window.location.href = "{{ url_for('contas.listar_contas') }}";
                } else {
                    alert(`Erro ao desativar conta: ${data.error}`);
                    desativarContaModal.hide();
                }
            });
        });
    }
    // --- ADIÇÃO V2.07: Funções globais para gerenciar contatos ---
    window.openEditContatoModal = (contatoId) => {
        const contato = contatosData.find(c => c.id === contatoId);
        if(contato) {
            document.getElementById('edit-contato-id').value = contato.id;
            document.getElementById('edit-contato-nome').value = contato.nome;
            document.getElementById('edit-contato-email').value = contato.email || '';
            document.getElementById('edit-contato-telefone').value = contato.telefone || '';
            document.getElementById('edit-contato-cargo').value = contato.cargo || '';
            editContatoModal.show();
        }
    };

    window.handleDeleteContato = (contatoId) => {
        if (confirm('Tem certeza que deseja desativar este contato?')) {
            fetch(`/api/contatos/${contatoId}`, { method: 'DELETE' })
            .then(res => res.json())
            .then(result => {
                if (result.success) {
                    populateDropdownsAndFetchDetails(); // Recarrega tudo
                } else {
                    alert(`Erro ao desativar contato: ${result.error}`);
                }
            });
        }
    };

    const toggleEditMode = (isEditing) => {
        formEditConta.querySelectorAll('input, select').forEach(field => {
            // Permite editar se CAN_EDIT_THIS_ACCOUNT for verdadeiro
            if (field.id === 'edit-owner' && !IS_ADMIN) {
                field.disabled = true; // O campo de dono só é editável pelo admin
            } else {
                field.disabled = !isEditing;
            }
        });

        editButtons.style.display = isEditing ? 'block' : 'none';
        btnEditConta.style.display = isEditing ? 'none' : 'block';
        hierarchyHr.style.display = isEditing ? 'none' : (hierarchyInfo.innerHTML ? 'block' : 'none');
        hierarchyInfo.style.display = isEditing ? 'none' : 'block';
        if (IS_ADMIN && adminFields) { adminFields.style.display = isEditing ? 'block' : 'none'; }
    };

    btnEditConta.addEventListener('click', () => {
    // Usa a nova variável para decidir se habilita a edição
    if (CAN_EDIT_THIS_ACCOUNT) {
        toggleEditMode(true);
    } else {
        alert("Você não tem permissão para editar esta conta.");
    }
    });
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
            matriz_id: matrizIdInput.value,
        };
        if (IS_ADMIN) {
            updatedData.owner_id = document.getElementById('edit-owner').value;
        }
        const response = await fetch(`/api/contas/${CONTA_ID}`, {
            method: 'PUT', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updatedData)
        });
        const result = await response.json();
        if (result.success) {
            document.querySelector('h1.text-azevix').innerHTML = `<i class="fas fa-building me-2"></i>${updatedData.nome_fantasia}`;
            await populateDropdownsAndFetchDetails();
            toggleEditMode(false);
            alert('Conta atualizada com sucesso!');
        } else { alert(`Falha ao atualizar: ${result.error || 'Erro desconhecido'}`); }
    });

    let searchTimeout;
    matrizSearchInput.addEventListener('keyup', () => {
        clearTimeout(searchTimeout);
        const term = matrizSearchInput.value;
        if (term.length < 3) { matrizResults.innerHTML = ''; return; }
        searchTimeout = setTimeout(() => {
            fetch(`/api/contas/search?term=${encodeURIComponent(term)}`)
                .then(res => res.json())
                .then(data => {
                    matrizResults.innerHTML = '';
                    if (data.success && data.contas.length > 0) {
                        data.contas.filter(c => c.id !== CONTA_ID).forEach(conta => {
                            const item = document.createElement('a');
                            item.href = '#';
                            item.className = 'list-group-item list-group-item-action';
                            item.textContent = `${conta.nome_fantasia}`;
                            item.addEventListener('click', (e) => {
                                e.preventDefault();
                                matrizSearchInput.value = conta.nome_fantasia;
                                matrizIdInput.value = conta.id;
                                matrizResults.innerHTML = '';
                            });
                            matrizResults.appendChild(item);
                        });
                    }
                });
        }, 500);
    });

    // --- ADIÇÃO V2.07: Listener para o formulário de edição de contato ---
    formEditContato.addEventListener('submit', async (e) => {
        e.preventDefault();
        const contatoId = document.getElementById('edit-contato-id').value;
        const updatedData = {
            nome: document.getElementById('edit-contato-nome').value,
            email: document.getElementById('edit-contato-email').value,
            telefone: document.getElementById('edit-contato-telefone').value,
            cargo: document.getElementById('edit-contato-cargo').value,
        };
        const response = await fetch(`/api/contatos/${contatoId}`, {
            method: 'PUT', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updatedData)
        });
        const result = await response.json();
        if (result.success) {
            editContatoModal.hide();
            await populateDropdownsAndFetchDetails();
        } else {
            alert(`Falha ao atualizar contato: ${result.error || 'Erro desconhecido'}`);
        }
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
            await populateDropdownsAndFetchDetails();
        } else { alert('Erro ao adicionar contato: ' + result.error); }
    });

    populateDropdownsAndFetchDetails();
});