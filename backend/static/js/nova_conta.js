document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById('novaContaForm');
    const alertContainer = document.getElementById('alert-container');

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        if (data.lead_valor) {
            data.lead_valor = parseFloat(data.lead_valor);
        }

        fetch('/api/contas', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
        .then(res => res.json())
        .then(result => {
            if (result.success) {
                // Redireciona para a lista de contas em caso de sucesso
                window.location.href = result.redirect_url;
            } else {
                // Mostra a mensagem de erro da API
                alertContainer.innerHTML = `<div class="alert alert-danger">${result.error}</div>`;
            }
        });
    });
});