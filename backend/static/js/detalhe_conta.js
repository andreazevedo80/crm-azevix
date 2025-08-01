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
    
    // --- ADIÇÃO v5.03: Elementos do Modal de Edição do Processo do Lead ---
    const editLeadProcessoModalEl = document.getElementById('editLeadProcessoModal');
    const editLeadProcessoModal = new bootstrap.Modal(editLeadProcessoModalEl);
    const formEditLeadProcesso = document.getElementById('form-edit-lead-processo');
    const leadStatusSelect = document.getElementById('edit-lead-status');
    const motivoPerdaContainer = document.getElementById('motivo-perda-container');
    const motivoPerdaSelect = document.getElementById('edit-lead-motivo-perda');
    
    // --- ADIÇÃO v6.0: Elementos do Modal de Nova Oportunidade ---
    const btnNovaOportunidade = document.getElementById('btn-nova-oportunidade');
    const novaOportunidadeModalEl = document.getElementById('novaOportunidadeModal');
    const novaOportunidadeModal = new bootstrap.Modal(novaOportunidadeModalEl);
    const formNovaOportunidade = document.getElementById('form-nova-oportunidade');
    
    // Estado da aplicação
    let originalContaData = {};
    let contatosData = [];
    let leadsData = []; // Armazena a lista de leads
    let statusLeadsOptions = []; // Para armazenar os status
    const motivosPerdaOptions = ['Preço', 'Concorrência', 'Timing', 'Sem Orçamento', 'Sem Fit com o Produto']; // Hardcoded por enquanto

    const populateSelect = (selectElement, options, selectedValue) => {
        selectElement.innerHTML = '';
        if (selectElement.id === 'edit-segmento') selectElement.add(new Option('Selecione...', ''));
        if (selectElement.id === 'edit-matriz') selectElement.add(new Option('Nenhuma', ''));
        if (selectElement.id === 'edit-lead-motivo-perda') selectElement.add(new Option('Selecione...', ''));
        
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

    // --- ALTERAÇÃO v5.03: Função renderLeads completamente reescrita ---
    const renderLeads = (leads) => {
        listaLeads.innerHTML = '';
        if (leads && leads.length > 0) {
            leads.forEach(l => {
                const tempIcons = `
                    <i class="fas fa-fire ${l.temperatura === 'Quente' ? 'text-danger' : 'text-muted'}" style="cursor: pointer;" onclick="updateTemperaturaLead(${l.id}, 'Quente')" title="Quente"></i>
                    <i class="fas fa-sun ${l.temperatura === 'Morno' ? 'text-warning' : 'text-muted'}" style="cursor: pointer;" onclick="updateTemperaturaLead(${l.id}, 'Morno')" title="Morno"></i>
                    <i class="fas fa-snowflake ${l.temperatura === 'Frio' ? 'text-info' : 'text-muted'}" style="cursor: pointer;" onclick="updateTemperaturaLead(${l.id}, 'Frio')" title="Frio"></i>
                `;
                const followupIcon = l.follow_up_necessario ? 'fa-flag text-danger' : 'fa-flag text-muted';

                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${l.titulo}</td>
                    <td><span class="badge bg-primary">${l.estagio_ciclo_vida}</span></td>
                    <td><span class="badge bg-info">${l.status_lead}</span></td>
                    <td class="text-center">${tempIcons}</td>
                    <td class="text-center">
                        <i class="fas ${followupIcon} fa-lg" style="cursor: pointer;" onclick="toggleFollowUp(${l.id}, ${!l.follow_up_necessario})" title="Marcar Follow-up"></i>
                    </td>
                    <td>
                        <button class="btn btn-sm btn-outline-secondary" onclick="openEditLeadProcessoModal(${l.id})">
                            <i class="fas fa-edit"></i> Alterar Status
                        </button>
                    </td>
                `;
                listaLeads.appendChild(row);
            });
        } else {
            listaLeads.innerHTML = '<tr><td colspan="6" class="text-center">Nenhuma oportunidade encontrada.</td></tr>';
        }
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

    // --- Função para renderizar o log de auditoria ---
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
        if (configData.success) { 
            populateSelect(document.getElementById('edit-segmento'), configData.segmentos);
            statusLeadsOptions = configData.status_leads; // Armazena a lista de status
        }

        if ((IS_ADMIN || IS_MANAGER) && adminFields) {
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
            leadsData = data.leads; // Armazena os leads
            renderInfoForm(originalContaData);
            renderContatos(data.contatos);
            renderLeads(data.leads);
            renderHierarchy(data.conta);
            
            // --- Chama a função para buscar o histórico ---
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

    // --- Funções globais para gerenciar contatos ---
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

    // --- Funções para gerenciar o processo do lead ---
    window.toggleFollowUp = (leadId, novoStatus) => {
        const data = { follow_up_necessario: novoStatus };
        fetch(`/api/leads/${leadId}/processo`, {
            method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data)
        }).then(() => populateDropdownsAndFetchDetails());
    };

    // --- ADIÇÃO v5.03: Nova função para atualizar temperatura do lead ---
    window.updateTemperaturaLead = (leadId, novaTemperatura) => {
        const data = { temperatura: novaTemperatura };
        fetch(`/api/leads/${leadId}/processo`, {
            method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data)
        }).then(() => populateDropdownsAndFetchDetails());
    };

    // --- ALTERAÇÃO v5.03: Função openEditLeadProcessoModal completada ---
    window.openEditLeadProcessoModal = (leadId) => {
        const lead = leadsData.find(l => l.id === leadId);
        if (lead) {
            formEditLeadProcesso.querySelector('#edit-lead-id').value = lead.id;
            formEditLeadProcesso.querySelector('#edit-lead-titulo').textContent = lead.titulo;
            
            // Popula os selects do modal
            populateSelect(leadStatusSelect, statusLeadsOptions, lead.status_lead);
            populateSelect(motivoPerdaSelect, motivosPerdaOptions, lead.motivo_perda);

            // Controla a visibilidade do motivo da perda
            const checkMotivoPerda = () => {
                const statusSelecionado = leadStatusSelect.value;
                if (statusSelecionado === 'Perdido' || statusSelecionado === 'Não Qualificado') {
                    motivoPerdaContainer.style.display = 'block';
                    motivoPerdaSelect.required = true;
                } else {
                    motivoPerdaContainer.style.display = 'none';
                    motivoPerdaSelect.required = false;
                }
            };
            
            leadStatusSelect.removeEventListener('change', checkMotivoPerda); // Remove listener antigo para evitar duplicação
            leadStatusSelect.addEventListener('change', checkMotivoPerda);
            checkMotivoPerda(); // Executa uma vez para o estado inicial

            editLeadProcessoModal.show();
        }
    };

    // --- Lógica para o modal de desativação ---
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
                    window.location.href = LISTAR_CONTAS_URL;
                } else {
                    alert(`Erro ao desativar conta: ${data.error}`);
                    desativarContaModal.hide();
                }
            });
        });
    }

    const toggleEditMode = (isEditing) => {
        formEditConta.querySelectorAll('input, select').forEach(field => {
            // Permite editar se CAN_EDIT_THIS_ACCOUNT for verdadeiro
            if (field.id === 'edit-owner') {
                field.disabled = !isEditing || !(IS_ADMIN || IS_MANAGER);
            } else {
                field.disabled = !isEditing;
            }
        });

        editButtons.style.display = isEditing ? 'block' : 'none';
        btnEditConta.style.display = isEditing ? 'none' : 'block';
        hierarchyHr.style.display = isEditing ? 'none' : (hierarchyInfo.innerHTML ? 'block' : 'none');
        hierarchyInfo.style.display = isEditing ? 'none' : 'block';
        if ((IS_ADMIN || IS_MANAGER) && adminFields) { adminFields.style.display = isEditing ? 'block' : 'none'; }
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

    // --- Listener para o formulário de edição de contato ---
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

    // --- ADIÇÃO v5.03: Listener para o formulário de edição de processo do lead ---
    formEditLeadProcesso.addEventListener('submit', async (e) => {
        e.preventDefault();
        const leadId = formEditLeadProcesso.querySelector('#edit-lead-id').value;
        const novoStatus = formEditLeadProcesso.querySelector('#edit-lead-status').value;
        
        const updatedData = { status_lead: novoStatus };
        
        if (novoStatus === 'Perdido' || novoStatus === 'Não Qualificado') {
            const motivo = formEditLeadProcesso.querySelector('#edit-lead-motivo-perda').value;
            if (!motivo) {
                alert('O motivo da perda é obrigatório.');
                return;
            }
            updatedData.motivo_perda = motivo;
        }
        
        const response = await fetch(`/api/leads/${leadId}/processo`, {
            method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(updatedData)
        });
        const result = await response.json();
        if (result.success) {
            editLeadProcessoModal.hide();
            await populateDropdownsAndFetchDetails();
        } else {
            alert(`Falha ao atualizar: ${result.error || 'Erro desconhecido'}`);
        }
    });

    // --- ADIÇÃO v6.0: Event Listeners para o fluxo de nova oportunidade ---
    if (btnNovaOportunidade) {
        btnNovaOportunidade.addEventListener('click', () => {
            novaOportunidadeModal.show();
        });

        formNovaOportunidade.addEventListener('submit', async (e) => {
            e.preventDefault();
            const novaOportunidadeData = {
                conta_id: CONTA_ID,
                titulo: formNovaOportunidade.querySelector('#nova-lead-titulo').value,
                valor_estimado: formNovaOportunidade.querySelector('#nova-lead-valor').value,
            };

            const response = await fetch('/api/leads', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(novaOportunidadeData)
            });
            const result = await response.json();

            if (result.success) {
                formNovaOportunidade.reset();
                novaOportunidadeModal.hide();
                await populateDropdownsAndFetchDetails(); // Recarrega a lista de leads
            } else {
                alert(`Erro ao criar oportunidade: ${result.error || 'Erro desconhecido'}`);
            }
        });
    }

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