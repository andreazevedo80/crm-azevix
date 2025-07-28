document.addEventListener('DOMContentLoaded', function() {
    const importForm = document.getElementById('importForm');
    const resultContainer = document.getElementById('result-container');
    const importAlert = document.getElementById('import-alert');
    const importErrors = document.getElementById('import-errors');
    const submitButton = importForm.querySelector('button[type="submit"]');

    importForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const fileInput = document.getElementById('csvFile');
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

        // Mostra o spinner e desabilita o botão
        submitButton.disabled = true;
        submitButton.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Processando...';
        resultContainer.style.display = 'none';

        fetch('/admin/api/import/csv', {
            method: 'POST',
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            resultContainer.style.display = 'block';
            if (data.success) {
                const { success_count, error_count, errors } = data.report;
                importAlert.className = 'alert alert-success';
                importAlert.innerHTML = `<strong>Importação Concluída:</strong> ${success_count} registros importados com sucesso.`;
                
                importErrors.innerHTML = '';
                if (error_count > 0) {
                    importAlert.className = 'alert alert-warning';
                    importAlert.innerHTML += ` ${error_count} registros continham erros.`;
                    
                    let errorListHTML = '<ul class="list-group">';
                    errors.forEach(err => {
                        errorListHTML += `<li class="list-group-item list-group-item-danger">${err}</li>`;
                    });
                    errorListHTML += '</ul>';
                    importErrors.innerHTML = errorListHTML;
                }
            } else {
                importAlert.className = 'alert alert-danger';
                importAlert.textContent = `Erro: ${data.error}`;
                importErrors.innerHTML = '';
            }
        })
        .catch(err => {
            resultContainer.style.display = 'block';
            importAlert.className = 'alert alert-danger';
            importAlert.textContent = 'Ocorreu um erro de rede. Tente novamente.';
            importErrors.innerHTML = '';
        })
        .finally(() => {
            submitButton.disabled = false;
            submitButton.innerHTML = '<i class="fas fa-upload me-1"></i> Iniciar Importação';
            importForm.reset();
        });
    });
});