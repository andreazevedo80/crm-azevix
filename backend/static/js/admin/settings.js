document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('settingsForm');
    const testSmtpBtn = document.getElementById('testSmtpBtn');
    const alertContainer = document.getElementById('alert-container');

    // Função para buscar e preencher as configurações
    const loadSettings = () => {
        fetch('/admin/api/settings')
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    for (const [key, value] of Object.entries(data.settings)) {
                        const field = form.querySelector(`#${key}`);
                        if (field) {
                            if (field.type === 'checkbox') {
                                field.checked = value === 'true' || value === true;
                            } else {
                                field.value = value || '';
                            }
                        }
                    }
                }
            });
    };

    // Função para exibir alertas
    const showAlert = (message, type = 'success') => {
        alertContainer.innerHTML = `<div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>`;
    };

    // Listener para salvar o formulário
    form.addEventListener('submit', function (e) {
        e.preventDefault();
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        
        // Trata o checkbox
        data.SMTP_USE_TLS = document.getElementById('SMTP_USE_TLS').checked;

        fetch('/admin/api/settings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
        .then(res => res.json())
        .then(result => {
            if (result.success) {
                showAlert('Configurações salvas com sucesso!');
            } else {
                showAlert(`Erro ao salvar: ${result.error}`, 'danger');
            }
        });
    });

    // Listener para o botão de teste SMTP
    testSmtpBtn.addEventListener('click', function () {
        const smtpData = {
            SMTP_SERVER: document.getElementById('SMTP_SERVER').value,
            SMTP_PORT: document.getElementById('SMTP_PORT').value,
            SMTP_USE_TLS: document.getElementById('SMTP_USE_TLS').checked,
            SMTP_USER: document.getElementById('SMTP_USER').value,
            SMTP_PASSWORD: document.getElementById('SMTP_PASSWORD').value,
        };

        testSmtpBtn.disabled = true;
        testSmtpBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Enviando...';

        fetch('/admin/api/settings/test-smtp', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(smtpData)
        })
        .then(res => res.json())
        .then(result => {
            if (result.success) {
                showAlert(result.message, 'success');
            } else {
                showAlert(result.error, 'danger');
            }
        })
        .finally(() => {
            testSmtpBtn.disabled = false;
            testSmtpBtn.textContent = 'Testar Conexão SMTP';
        });
    });

    // Carga inicial
    loadSettings();
});