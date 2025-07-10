document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById('novaContaForm');
    const alertContainer = document.getElementById('alert-container');

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        // Converte o valor para número, se existir
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
                window.location.href = '/contas';
            } else {
                alertContainer.innerHTML = `<div class="alert alert-danger">${result.error}</div>`;
            }
        });
    });
});