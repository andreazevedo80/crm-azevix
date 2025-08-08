document.addEventListener('DOMContentLoaded', function() {
    const tableBody = document.getElementById('itens-proposta-table');
    const subtotalEl = document.getElementById('subtotal-proposta');
    const formAddItem = document.getElementById('form-add-item');
    const catalogoSelect = document.getElementById('item-catalogo');
    const descricaoInput = document.getElementById('item-descricao');
    const valorInput = document.getElementById('item-valor');
    const custosTableBody = document.getElementById('custos-proposta-table');
    const formAddCusto = document.getElementById('form-add-custo');
    const summaryValorTotal = document.getElementById('summary-valor-total');
    const summaryCustoTotal = document.getElementById('summary-custo-total');
    const summaryLucroLiquido = document.getElementById('summary-lucro-liquido');
    
    // --- ADIÇÃO v11.2: Constantes para Ciclo de Vida ---
    const statusSelect = document.getElementById('proposta-status');
    const dataEnvioInput = document.getElementById('proposta-data-envio');
    const dataValidadeInput = document.getElementById('proposta-data-validade');
    const btnSaveStatus = document.getElementById('btn-save-status');
    const btnDuplicate = document.getElementById('btn-duplicate-proposta');

    let catalogoItems = [];
    let currentItens = [];
    let currentCustos = [];

    const formatCurrency = (value) => {
        return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);
    };

    const renderItens = (itens, subtotal) => {
        tableBody.innerHTML = '';
        itens.forEach(item => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${item.descricao}</td>
                <td class="text-center">${item.quantidade}</td>
                <td class="text-end">${formatCurrency(item.valor_unitario)}</td>
                <td class="text-end">${formatCurrency(item.valor_total)}</td>
                <td><button class="btn btn-sm btn-outline-danger" onclick="handleDeleteItem(${item.id})"><i class="fas fa-trash"></i></button></td>
            `;
            tableBody.appendChild(row);
        });
        subtotalEl.textContent = formatCurrency(subtotal);
    };

    // --- Função para renderizar a tabela de custos ---
    const renderCustos = (custos) => {
        custosTableBody.innerHTML = '';
        custos.forEach(custo => {
            const valorFormatado = custo.tipo_custo === 'Percentual' ? `${custo.valor}%` : formatCurrency(custo.valor);
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${custo.descricao}</td>
                <td class="text-end">${valorFormatado}</td>
                <td><button class="btn btn-sm btn-outline-danger" onclick="handleDeleteCusto(${custo.id})"><i class="fas fa-trash"></i></button></td>
            `;
            custosTableBody.appendChild(row);
        });
    };

    // --- Função para calcular e exibir o resumo financeiro ---
    const calcularResumoFinanceiro = () => {
        const valorTotalProposta = currentItens.reduce((sum, item) => sum + parseFloat(item.valor_total), 0);
        
        let custoTotal = 0;
        currentCustos.forEach(custo => {
            if (custo.tipo_custo === 'Fixo') {
                custoTotal += parseFloat(custo.valor);
            } else { // Percentual
                custoTotal += valorTotalProposta * (parseFloat(custo.valor) / 100);
            }
        });

        const lucroLiquido = valorTotalProposta - custoTotal;

        summaryValorTotal.textContent = formatCurrency(valorTotalProposta);
        summaryCustoTotal.textContent = formatCurrency(custoTotal);
        summaryLucroLiquido.textContent = formatCurrency(lucroLiquido);
        summaryLucroLiquido.className = `card-title ${lucroLiquido >= 0 ? 'text-primary' : 'text-danger'}`;
    };
    
    const fetchDetails = () => {
        fetch(`/api/propostas/${PROPOSTA_ID}/details`)
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    currentItens = data.itens;
                    currentCustos = data.custos;
                    renderItens(data.itens, data.proposta.valor_total);
                    renderCustos(data.custos);
                    calcularResumoFinanceiro();
                    catalogoItems = data.catalogo;
                    
                    catalogoSelect.innerHTML = '<option value="">Selecione do catálogo...</option>';
                    catalogoItems.forEach(item => {
                        catalogoSelect.add(new Option(item.nome, item.id));
                    });
                    
                    // --- ADIÇÃO v11.2: Preenche os campos do ciclo de vida ---
                    statusSelect.value = data.proposta.status;
                    dataEnvioInput.value = data.proposta.data_envio;
                    dataValidadeInput.value = data.proposta.data_validade;
                    
                    // Desabilita a edição se a proposta não estiver em elaboração
                    const isEditable = data.proposta.status === 'Em elaboração';
                    formAddItem.querySelectorAll('input, select, button').forEach(el => el.disabled = !isEditable);
                    formAddCusto.querySelectorAll('input, select, button').forEach(el => el.disabled = !isEditable);
                }
            });
    };

    catalogoSelect.addEventListener('change', () => {
        const selectedId = catalogoSelect.value;
        if (selectedId) {
            const item = catalogoItems.find(i => i.id == selectedId);
            if (item) {
                descricaoInput.value = item.nome;
                valorInput.value = item.preco_sob_consulta ? '' : parseFloat(item.preco_base).toFixed(2);
            }
        }
    });

    formAddItem.addEventListener('submit', (e) => {
        e.preventDefault();
        const data = {
            produto_servico_id: catalogoSelect.value || null,
            descricao: descricaoInput.value,
            quantidade: document.getElementById('item-qtd').value,
            valor_unitario: valorInput.value,
        };

        fetch(`/api/propostas/${PROPOSTA_ID}/items`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
        .then(res => res.json())
        .then(result => {
            if (result.success) {
                formAddItem.reset();
                fetchDetails(); // Recarrega a lista de itens
            } else {
                alert(`Erro: ${result.error}`);
            }
        });
    });

    // --- Função para deletar um item ---
    window.handleDeleteItem = (itemId) => {
        if (confirm('Tem certeza que deseja remover este item da proposta?')) {
            fetch(`/api/propostas/items/${itemId}`, {
                method: 'DELETE'
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    fetchDetails(); // Recarrega a lista de itens e o subtotal
                } else {
                    alert(`Erro ao remover o item: ${data.error}`);
                }
            });
        }
    };

    // --- Lógica para adicionar e deletar custos ---
    formAddCusto.addEventListener('submit', (e) => {
        e.preventDefault();
        const data = {
            descricao: document.getElementById('custo-descricao').value,
            tipo_custo: document.getElementById('custo-tipo').value,
            valor: document.getElementById('custo-valor').value,
        };

        fetch(`/api/propostas/${PROPOSTA_ID}/custos`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
        .then(res => res.json())
        .then(result => {
            if (result.success) {
                formAddCusto.reset();
                fetchDetails();
            } else {
                alert(`Erro: ${result.error}`);
            }
        });
    });

    window.handleDeleteCusto = (custoId) => {
        if (confirm('Tem certeza que deseja remover este custo?')) {
            fetch(`/api/propostas/custos/${custoId}`, { method: 'DELETE' })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        fetchDetails();
                    } else {
                        alert(`Erro ao remover custo: ${data.error}`);
                    }
                });
        }
    };

    // --- ADIÇÃO v11.2: Listeners para o ciclo de vida ---
    btnSaveStatus.addEventListener('click', () => {
        const data = {
            status: statusSelect.value,
            data_envio: dataEnvioInput.value,
            data_validade: dataValidadeInput.value
        };
        fetch(`/api/propostas/${PROPOSTA_ID}/status`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        }).then(() => fetchDetails());
    });

    btnDuplicate.addEventListener('click', () => {
        if (confirm('Isso criará uma nova versão desta proposta. Deseja continuar?')) {
            fetch(`/api/propostas/${PROPOSTA_ID}/duplicate`, { method: 'POST' })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        window.location.href = data.redirect_url;
                    } else {
                        alert(`Erro ao duplicar: ${data.error}`);
                    }
                });
        }
    });

    fetchDetails();
});