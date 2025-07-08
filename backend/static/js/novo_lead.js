document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById('leadForm');
    const alertContainer = document.getElementById('alert-container');
    const segmentoSelect = document.getElementById('segmento');

    // Popula o select de segmentos (código existente)
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

    // Listener do formulário (MODIFICADO)
    form.addEventListener('submit', function(event) {
        event.preventDefault(); // Impede o recarregamento da página

        // ---- A GRANDE MUDANÇA ESTÁ AQUI ----
        // 1. Usamos FormData para coletar todos os campos do formulário de forma segura.
        // Ele usa os atributos 'name' dos inputs.
        const formData = new FormData(form);

        // 2. Convertemos os dados do formulário para um objeto simples.
        const leadData = Object.fromEntries(formData.entries());
        // ------------------------------------

        fetch('/api/leads', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(leadData) // Enviamos o objeto como JSON
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Sucesso! Redireciona para a lista de leads.
                window.location.href = '/leads';
            } else {
                // Exibe o erro retornado pela API.
                showAlert(data.error || 'Não foi possível salvar o lead.', 'danger');
            }
        })
        .catch(error => {
            console.error('Erro na requisição:', error);
            showAlert('Erro de conexão! Verifique sua rede e tente novamente.', 'danger');
        });
    });

    function showAlert(message, type) {
        alertContainer.innerHTML = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
    }
});