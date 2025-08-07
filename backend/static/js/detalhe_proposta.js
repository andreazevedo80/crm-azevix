document.addEventListener('DOMContentLoaded', function() {
    const tableBody = document.getElementById('itens-proposta-table');
    const subtotalEl = document.getElementById('subtotal-proposta');
    const formAddItem = document.getElementById('form-add-item');
    const catalogoSelect = document.getElementById('item-catalogo');
    const descricaoInput = document.getElementById('item-descricao');
    const valorInput = document.getElementById('item-valor');

    let catalogoItems = [];

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
                <td><button class="btn btn-sm btn-outline-danger"><i class="fas fa-trash"></i></button></td>
            `;
            tableBody.appendChild(row);
        });
        subtotalEl.textContent = formatCurrency(subtotal);
    };
    
    const fetchDetails = () => {
        fetch(`/api/propostas/${PROPOSTA_ID}/details`)
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    renderItens(data.itens, data.proposta.valor_total);
                    catalogoItems = data.catalogo;
                    
                    catalogoSelect.innerHTML = '<option value="">Selecione do catálogo...</option>';
                    catalogoItems.forEach(item => {
                        catalogoSelect.add(new Option(item.nome, item.id));
                    });
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

    fetchDetails();
});