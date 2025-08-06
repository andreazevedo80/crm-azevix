document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('activity-form');
    const formTitle = document.getElementById('form-title-activity');
    const activityIdInput = document.getElementById('activity-id');
    const nomeInput = document.getElementById('activity-nome');
    const descricaoInput = document.getElementById('activity-descricao');
    const horasInput = document.getElementById('activity-horas');
    const cancelBtn = document.getElementById('cancel-btn-activity');
    const tableBody = document.getElementById('activities-table-body');

    let currentActivities = [];

    const renderTable = () => {
        tableBody.innerHTML = '';
        currentActivities.forEach(activity => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><strong>${activity.nome}</strong><br><small class="text-muted">${activity.descricao || ''}</small></td>
                <td>${activity.horas_estimadas}</td>
                <td><span class="badge bg-${activity.is_active ? 'success' : 'danger'}">${activity.is_active ? 'Ativa' : 'Inativa'}</span></td>
                <td>
                    <button class="btn btn-sm btn-outline-secondary" onclick="handleEdit(${activity.id})"><i class="fas fa-pencil-alt"></i></button>
                    <button class="btn btn-sm btn-outline-${activity.is_active ? 'danger' : 'success'}" onclick="handleToggleActive(${activity.id}, ${!activity.is_active})"><i class="fas ${activity.is_active ? 'fa-toggle-off' : 'fa-toggle-on'}"></i></button>
                </td>
            `;
            tableBody.appendChild(row);
        });
    };

    const fetchActivities = () => {
        fetch('/admin/api/activities')
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    currentActivities = data.activities;
                    renderTable();
                }
            });
    };
    
    const resetForm = () => {
        form.reset();
        activityIdInput.value = '';
        formTitle.textContent = 'Adicionar Nova Atividade';
        cancelBtn.style.display = 'none';
    };

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const id = activityIdInput.value;
        const data = {
            nome: nomeInput.value,
            descricao: descricaoInput.value,
            horas_estimadas: horasInput.value
        };
        
        const url = id ? `/admin/api/activities/${id}` : '/admin/api/activities';
        const method = id ? 'PUT' : 'POST';

        fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
        .then(res => res.json())
        .then(result => {
            if(result.success) {
                fetchActivities();
                resetForm();
            } else {
                alert(`Erro: ${result.error}`);
            }
        });
    });

    window.handleEdit = (id) => {
        const activity = currentActivities.find(a => a.id === id);
        if (activity) {
            formTitle.textContent = 'Editar Atividade';
            activityIdInput.value = activity.id;
            nomeInput.value = activity.nome;
            descricaoInput.value = activity.descricao;
            horasInput.value = activity.horas_estimadas;
            cancelBtn.style.display = 'inline-block';
            window.scrollTo(0, 0);
        }
    };
    
    window.handleToggleActive = (id, newStatus) => {
        const activity = currentActivities.find(a => a.id === id);
        fetch(`/admin/api/activities/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ...activity, is_active: newStatus })
        })
        .then(res => res.json())
        .then(data => {
            if(data.success) {
                fetchActivities();
            }
        });
    };

    cancelBtn.addEventListener('click', resetForm);
    fetchActivities();
});