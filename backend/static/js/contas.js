document.addEventListener("DOMContentLoaded", function() {
    // --- ELEMENTOS DA PÁGINA ---
    const displayArea = document.getElementById('contas-display-area');
    const checkModalInput = document.getElementById('check-conta-input');
    const checkResultsContainer = document.getElementById('check-results-container');
    const proceedButton = document.getElementById('proceed-to-register-btn');
    const checkModalEl = document.getElementById('checkContaModal');

    const loadingSpinner = `<div class="text-center py-5"><div class="spinner-border text-azevix" role="status"></div></div>`;

    // --- FUNÇÕES ---

    const renderContas = () => {
        displayArea.innerHTML = loadingSpinner;
        fetch('/api/contas')
            .then(res => res.json())
            .then(data => {
                let tableContent = '';
                if (data.success && data.contas.length > 0) {
                    const rows = data.contas.map(conta => `
                        <tr>
                            <td>${conta.nome_fantasia}</td>
                            <td>${conta.cnpj || '-'}</td>
                            <td><span class="badge bg-secondary">${conta.tipo_conta}</span></td>
                            <td>${conta.segmento || '-'}</td>
                            <td>${conta.owner_name}</td>
                            <td><a href="#" class="btn btn-sm btn-outline-primary disabled">Detalhes</a></td>
                        </tr>`).join('');
                    tableContent = `<div class="table-responsive"><table class="table table-hover"><thead><tr><th>Nome Fantasia</th><th>CNPJ</th><th>Tipo</th><th>Segmento</th><th>Responsável</th><th>Ações</th></tr></thead><tbody>${rows}</tbody></table></div>`;
                } else {
                    tableContent = `<p class="text-center py-4">Nenhuma conta encontrada.</p>`;
                }
                displayArea.innerHTML = tableContent;
            });
    };

    const checkDuplicates = () => {
        const term = checkModalInput.value;
        proceedButton.style.display = 'none';

        if (term.length < 3) {
            checkResultsContainer.innerHTML = `<p class="text-muted">Digite pelo menos 3 caracteres.</p>`;
            return;
        }

        checkResultsContainer.innerHTML = `<div class="spinner-border spinner-border-sm" role="status"></div> Buscando...`;
        fetch(`/api/contas/search?term=${encodeURIComponent(term)}`)
            .then(res => res.json())
            .then(data => {
                if (data.success && data.contas.length > 0) {
                    let resultsHtml = '<p class="text-danger"><strong>Atenção!</strong> Contas similares encontradas:</p><ul class="list-group">';
                    data.contas.forEach(conta => {
                        resultsHtml += `<li class="list-group-item"><strong>${conta.nome_fantasia}</strong> (CNPJ: ${conta.cnpj || 'N/A'}) - Responsável: <strong>${conta.owner_name}</strong></li>`;
                    });
                    resultsHtml += '</ul>';
                    checkResultsContainer.innerHTML = resultsHtml;
                } else {
                    checkResultsContainer.innerHTML = `<p class="text-success">Nenhuma conta encontrada com este termo. Pode prosseguir.</p>`;
                    proceedButton.style.display = 'inline-block';
                }
            });
    };

    // --- EVENT LISTENERS ---
    
    // Limpa o modal quando ele é fechado para a próxima busca
    checkModalEl.addEventListener('hidden.bs.modal', function () {
        checkModalInput.value = '';
        checkResultsContainer.innerHTML = '';
        proceedButton.style.display = 'none';
    });
    
    // Inicia a busca no modal após o usuário parar de digitar
    let checkTimeout;
    checkModalInput.addEventListener('keyup', () => {
        clearTimeout(checkTimeout);
        checkTimeout = setTimeout(checkDuplicates, 500);
    });

    // --- CARGA INICIAL ---
    renderContas();
});