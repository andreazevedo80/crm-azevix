document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById('novaContaForm');
    const alertContainer = document.getElementById('alert-container');
    const segmentoSelect = document.getElementById('segmento');
    const matrizSearchInput = document.getElementById('matriz_search');
    const matrizIdInput = document.getElementById('matriz_id');
    const matrizResults = document.getElementById('matriz-search-results');

    fetch('/api/contas/config')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.segmentos) {
                data.segmentos.forEach(seg => segmentoSelect.add(new Option(seg, seg)));
            }
        });
    
    let searchTimeout;
    matrizSearchInput.addEventListener('keyup', () => {
        clearTimeout(searchTimeout);
        const term = matrizSearchInput.value;
        matrizIdInput.value = ''; // Limpa o ID se o usuário está digitando
        if (term.length < 3) {
            matrizResults.innerHTML = '';
            return;
        }
        searchTimeout = setTimeout(() => {
            fetch(`/api/contas/search?term=${encodeURIComponent(term)}`)
                .then(res => res.json())
                .then(data => {
                    matrizResults.innerHTML = '';
                    if (data.success && data.contas.length > 0) {
                        data.contas.forEach(conta => {
                            const item = document.createElement('a');
                            item.href = '#';
                            item.className = 'list-group-item list-group-item-action';
                            item.textContent = `${conta.nome_fantasia} (CNPJ: ${conta.cnpj || 'N/A'})`;
                            item.addEventListener('click', (e) => {
                                e.preventDefault();
                                matrizSearchInput.value = conta.nome_fantasia;
                                matrizIdInput.value = conta.id;
                                matrizResults.innerHTML = '';
                            });
                            matrizResults.appendChild(item);
                        });
                    } else {
                        matrizResults.innerHTML = '<div class="list-group-item disabled">Nenhuma conta encontrada.</div>';
                    }
                });
        }, 500);
    });

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        if (data.lead_valor) data.lead_valor = parseFloat(data.lead_valor);
        fetch('/api/contas', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
        .then(res => res.json())
        .then(result => {
            if (result.success) {
                window.location.href = result.redirect_url;
            } else {
                alertContainer.innerHTML = `<div class="alert alert-danger">${result.error}</div>`;
            }
        });
    });
});