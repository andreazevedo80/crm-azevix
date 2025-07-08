document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById('leadForm');
    const alertContainer = document.getElementById('alert-container');
    const segmentoSelect = document.getElementById('segmento');

    // Popula o select de segmentos
    fetch('/api/config')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.segmentos) {
                data.segmentos.forEach(seg => {
                    const option = new Option(seg, seg);
                    segmentoSelect.add(option);
                });
            }
        });

    form.addEventListener('submit', function(event) {
        event.preventDefault();

        const leadData = {
            nome_completo: document.getElementById('nome_completo').value,
            nome_conta: document.getElementById('nome_conta').value,
            email: document.getElementById('email').value,
            telefone_celular: document.getElementById('telefone_celular').value,
            segmento: document.getElementById('segmento').value,
            observacoes: document.getElementById('observacoes').value,
        };

        fetch('/api/leads', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(leadData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.href = '/leads'; // Redireciona para a lista de leads
            } else {
                alertContainer.innerHTML = `
                    <div class="alert alert-danger alert-dismissible fade show" role="alert">
                        <strong>Erro!</strong> ${data.error || 'Não foi possível salvar o lead.'}
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            alertContainer.innerHTML = `
                <div class="alert alert-danger alert-dismissible fade show" role="alert">
                    <strong>Erro de conexão!</strong> Verifique sua rede e tente novamente.
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                </div>
            `;
        });
    });
});