document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById('novaContaForm');
    const alertContainer = document.getElementById('alert-container');
    const segmentoSelect = document.getElementById('segmento');

    // Popula o select de segmentos
    fetch('/api/contas/config')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.segmentos) {
                data.segmentos.forEach(seg => {
                    segmentoSelect.add(new Option(seg, seg));
                });
            }
        });

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
                window.location.href = result.redirect_url;
            } else {
                alertContainer.innerHTML = `<div class="alert alert-danger">${result.error}</div>`;
            }
        });
    });
});