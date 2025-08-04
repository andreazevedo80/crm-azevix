document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('loss-reason-form');
    const formTitle = document.getElementById('form-title-lr');
    const reasonIdInput = document.getElementById('lr-id');
    const reasonMotivoInput = document.getElementById('lr-motivo');
    const cancelBtn = document.getElementById('cancel-btn-lr');
    const tableBody = document.getElementById('loss-reasons-table-body');
    const applyDefaultsBtn = document.getElementById('apply-defaults-btn-lr');

    let currentReasons = [];

    const renderTable = () => {
        tableBody.innerHTML = '';
        currentReasons.forEach(reason => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${reason.motivo}</td>
                <td>
                    <span class="badge bg-${reason.is_active ? 'success' : 'danger'}">
                        ${reason.is_active ? 'Ativo' : 'Inativo'}
                    </span>
                </td>
                <td>
                    <button class="btn btn-sm btn-outline-secondary" onclick="handleEdit(${reason.id})"><i class="fas fa-pencil-alt"></i></button>
                    <button class="btn btn-sm btn-outline-${reason.is_active ? 'danger' : 'success'}" onclick="handleToggleActive(${reason.id}, ${!reason.is_active})">
                        <i class="fas ${reason.is_active ? 'fa-toggle-off' : 'fa-toggle-on'}"></i>
                    </button>
                </td>
            `;
            tableBody.appendChild(row);
        });
    };

    const fetchReasons = () => {
        fetch('/admin/api/loss-reasons')
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    currentReasons = data.reasons;
                    renderTable();
                }
            });
    };
    
    const resetForm = () => {
        form.reset();
        reasonIdInput.value = '';
        formTitle.textContent = 'Adicionar Novo Motivo';
        cancelBtn.style.display = 'none';
    };

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const id = reasonIdInput.value;
        const motivo = reasonMotivoInput.value;
        
        const url = id ? `/admin/api/loss-reasons/${id}` : '/admin/api/loss-reasons';
        const method = id ? 'PUT' : 'POST';

        fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ motivo: motivo })
        })
        .then(res => res.json())
        .then(data => {
            if(data.success) {
                fetchReasons();
                resetForm();
            } else {
                alert(`Erro: ${data.error}`);
            }
        });
    });

    window.handleEdit = (id) => {
        const reason = currentReasons.find(r => r.id === id);
        if (reason) {
            formTitle.textContent = 'Editar Motivo de Perda';
            reasonIdInput.value = reason.id;
            reasonMotivoInput.value = reason.motivo;
            cancelBtn.style.display = 'inline-block';
        }
    };
    
    window.handleToggleActive = (id, newStatus) => {
        const reason = currentReasons.find(r => r.id === id);
        fetch(`/admin/api/loss-reasons/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ is_active: newStatus, motivo: reason.motivo })
        })
        .then(res => res.json())
        .then(data => {
            if(data.success) {
                fetchReasons();
            }
        });
    };

    cancelBtn.addEventListener('click', resetForm);

    applyDefaultsBtn.addEventListener('click', () => {
        if (confirm('Isso adicionará os motivos de perda padrão do sistema que ainda não existirem. Deseja continuar?')) {
            fetch('/admin/api/loss-reasons/apply-defaults', { method: 'POST' })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        alert(data.message);
                        fetchReasons(); // Recarrega a tabela
                    } else {
                        alert(`Erro: ${data.error}`);
                    }
                });
        }
    });    


    fetchReasons();
});