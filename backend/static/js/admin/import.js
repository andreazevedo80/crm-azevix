document.addEventListener('DOMContentLoaded', function() {
    const uploadStep = document.getElementById('upload-step');
    const previewStep = document.getElementById('preview-step');
    const uploadForm = document.getElementById('uploadForm');
    const fileInput = document.getElementById('csvFile');
    const submitButton = uploadForm.querySelector('button[type="submit"]');

    const previewAlert = document.getElementById('preview-alert');
    const previewErrors = document.getElementById('preview-errors');
    const previewTableHead = document.getElementById('preview-table-head');
    const previewTableBody = document.getElementById('preview-table-body');
    const confirmBtn = document.getElementById('confirm-import-btn');
    const cancelBtn = document.getElementById('cancel-import-btn');

    let validDataToImport = [];

    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const file = fileInput.files[0];
        if (!file) {
            alert('Por favor, selecione um arquivo.');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        submitButton.disabled = true;
        submitButton.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Validando...';

        fetch('/admin/api/import/preview', {
            method: 'POST',
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                const { report, preview_data, headers } = data;
                validDataToImport = preview_data;
                
                // Exibe relatório
                previewAlert.className = `alert alert-${report.error_count > 0 ? 'warning' : 'success'}`;
                previewAlert.innerHTML = `<strong>Validação Concluída:</strong> ${report.success_count} registros prontos para importar. ${report.error_count} registros com erros.`;
                
                // Exibe erros
                previewErrors.innerHTML = '';
                if (report.errors.length > 0) {
                    let errorListHTML = '<p><strong>Erros encontrados:</strong></p><ul class="list-group">';
                    report.errors.forEach(err => {
                        errorListHTML += `<li class="list-group-item list-group-item-danger">${err}</li>`;
                    });
                    errorListHTML += '</ul>';
                    previewErrors.innerHTML = errorListHTML;
                }

                // Exibe preview
                previewTableHead.innerHTML = `<tr>${headers.map(h => `<th>${h}</th>`).join('')}</tr>`;
                previewTableBody.innerHTML = preview_data.map(row => `<tr>${headers.map(h => `<td>${row[h] || ''}</td>`).join('')}</tr>`).join('');

                uploadStep.style.display = 'none';
                previewStep.style.display = 'block';
                confirmBtn.disabled = report.success_count === 0;
            } else {
                alert(`Erro na validação: ${data.error}`);
            }
        })
        .finally(() => {
            submitButton.disabled = false;
            submitButton.innerHTML = '<i class="fas fa-eye me-1"></i> Validar e Ver Preview';
        });
    });

    cancelBtn.addEventListener('click', () => {
        uploadStep.style.display = 'block';
        previewStep.style.display = 'none';
        uploadForm.reset();
    });

    confirmBtn.addEventListener('click', () => {
        confirmBtn.disabled = true;
        confirmBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Importando...';

        fetch('/admin/api/import/execute', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ data: validDataToImport, filename: fileInput.files[0].name })
        })
        .then(res => res.json())
        .then(data => {
            if(data.success) {
                alert('Importação concluída com sucesso!');
                window.location.href = '/admin/imports'; // Redireciona para o histórico
            } else {
                alert(`Erro na importação: ${data.error}`);
            }
        })
        .finally(() => {
            confirmBtn.disabled = false;
            confirmBtn.textContent = 'Confirmar e Importar';
        });
    });
});