document.addEventListener("DOMContentLoaded", function() {
    const infoContaBody = document.getElementById('info-conta-body');
    const listaContatos = document.getElementById('lista-contatos');
    const listaLeads = document.getElementById('lista-leads');
    const formNovoContato = document.getElementById('form-novo-contato');

    const renderInfoConta = (conta) => {
        infoContaBody.innerHTML = `
            <p><strong>Razão Social:</strong> ${conta.razao_social || 'N/A'}</p>
            <p><strong>CNPJ:</strong> ${conta.cnpj || 'N/A'}</p>
            <p><strong>Tipo:</strong> ${conta.tipo_conta}</p>
            <p><strong>Segmento:</strong> ${conta.segmento || 'N/A'}</p>
            <p><strong>Responsável:</strong> ${conta.owner_name}</p>`;
    };

    const renderContatos = (contatos) => {
        listaContatos.innerHTML = '';
        if (contatos.length > 0) {
            contatos.forEach(c => {
                listaContatos.innerHTML += `<li class="list-group-item"><strong>${c.nome}</strong> (${c.cargo || 'N/A'})<br><small class="text-muted">${c.email || ''} | ${c.telefone || ''}</small></li>`;
            });
        } else {
            listaContatos.innerHTML = '<li class="list-group-item text-center">Nenhum contato cadastrado.</li>';
        }
    };

    const renderLeads = (leads) => {
        listaLeads.innerHTML = '';
        if (leads.length > 0) {
            leads.forEach(l => {
                listaLeads.innerHTML += `<tr><td>${l.titulo}</td><td><span class="badge bg-info">${l.status_lead}</span></td><td>${l.valor_estimado}</td><td>${l.contato_principal_nome}</td><td><a href="#" class="btn btn-sm btn-outline-secondary disabled">Ver</a></td></tr>`;
            });
        } else {
            listaLeads.innerHTML = '<tr><td colspan="5" class="text-center">Nenhuma oportunidade encontrada.</td></tr>';
        }
    };

    const fetchDetalhesConta = () => {
        if (typeof CONTA_ID === 'undefined') return;
        fetch(`/api/contas/${CONTA_ID}/details`)
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    renderInfoConta(data.conta);
                    renderContatos(data.contatos);
                    renderLeads(data.leads);
                }
            });
    };

    formNovoContato.addEventListener('submit', function(e) {
        e.preventDefault();
        const nome = document.getElementById('novo-contato-nome').value;
        if (!nome) { alert('O nome do contato é obrigatório.'); return; }
        
        const novoContatoData = {
            nome,
            email: document.getElementById('novo-contato-email').value,
            telefone: document.getElementById('novo-contato-telefone').value,
            cargo: document.getElementById('novo-contato-cargo').value
        };

        fetch(`/api/contas/${CONTA_ID}/contatos`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(novoContatoData)
        })
        .then(res => res.json())
        .then(result => {
            if (result.success) {
                formNovoContato.reset();
                fetchDetalhesConta();
            } else {
                alert('Erro ao adicionar contato: ' + result.error);
            }
        });
    });

    fetchDetalhesConta();
});