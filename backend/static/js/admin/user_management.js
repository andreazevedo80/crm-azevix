// --- ADIÇÃO v5.01: Lógica para a página de Gestão de Usuários ---

const editUserModalEl = document.getElementById('editUserModal');
const editUserModal = new bootstrap.Modal(editUserModalEl);
const formEditUser = document.getElementById('form-edit-user');
// --- Elementos do Modal de Convite ---
const inviteUserModalEl = document.getElementById('inviteUserModal');
const inviteUserModal = new bootstrap.Modal(inviteUserModalEl);
const formInviteUser = document.getElementById('form-invite-user');

// Função para popular selects, incluindo 'multiple'
const populateSelect = (selectElement, options, selectedValues = []) => {
    selectElement.innerHTML = '';
    if (selectElement.id === 'edit-user-gerente') {
        selectElement.add(new Option('Nenhum', ''));
    }
    
    const selectedSet = new Set(selectedValues);

    options.forEach(opt => {
        const option = new Option(opt.name, opt.id);
        if (selectedSet.has(opt.id)) {
            option.selected = true;
        }
        selectElement.add(option);
    });
};

// Abre o modal de edição
window.openEditUserModal = (userId) => {
    fetch(`/admin/api/users/${userId}`)
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                const { user, all_roles, all_managers } = data;
                formEditUser.querySelector('#edit-user-id').value = user.id;
                formEditUser.querySelector('#edit-user-name').value = user.name;
                formEditUser.querySelector('#edit-user-email').value = user.email;
                
                populateSelect(formEditUser.querySelector('#edit-user-roles'), all_roles, user.roles);
                populateSelect(formEditUser.querySelector('#edit-user-gerente'), all_managers, [user.gerente_id]);

                editUserModal.show();
            }
        });
};

// Salva as alterações do usuário
formEditUser.addEventListener('submit', (e) => {
    e.preventDefault();
    const userId = formEditUser.querySelector('#edit-user-id').value;
    const selectedRoles = Array.from(formEditUser.querySelector('#edit-user-roles').selectedOptions).map(opt => opt.value);

    const updatedData = {
        name: formEditUser.querySelector('#edit-user-name').value,
        email: formEditUser.querySelector('#edit-user-email').value,
        roles: selectedRoles,
        gerente_id: formEditUser.querySelector('#edit-user-gerente').value
    };

    fetch(`/admin/api/users/${userId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updatedData)
    })
    .then(res => res.json())
    .then(result => {
        if(result.success) {
            editUserModal.hide();
            window.location.reload(); // Recarrega a página para ver as alterações
        } else {
            alert(`Erro: ${result.error}`);
        }
    });
});

// Ativa/Desativa um usuário
window.toggleUserStatus = (userId) => {
    const confirmation = confirm('Tem certeza que deseja alterar o status deste usuário?');
    if(confirmation) {
        fetch(`/admin/api/users/${userId}/toggle-status`, {
            method: 'POST'
        })
        .then(res => res.json())
        .then(result => {
            if(result.success) {
                window.location.reload();
            } else {
                alert(`Erro: ${result.error}`);
            }
        });
    }
};
// --- ADIÇÃO v7.1: Abre e prepara o modal de convite ---
document.querySelector('[data-bs-target="#inviteUserModal"]').addEventListener('click', () => {
    // Busca a lista de roles para popular o select
    fetch('/admin/api/users/1') // Usamos o usuário 1 (admin) como base para pegar a lista de roles
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                const rolesSelect = formInviteUser.querySelector('#invite-user-roles');
                populateSelect(rolesSelect, data.all_roles);
            }
        });
});

// --- ADIÇÃO v7.1: Listener para o formulário de convite ---
formInviteUser.addEventListener('submit', (e) => {
    e.preventDefault();
    const alertContainer = formInviteUser.querySelector('#invite-alert-container');
    const submitButton = formInviteUser.querySelector('button[type="submit"]');
    
    const selectedRoles = Array.from(formInviteUser.querySelector('#invite-user-roles').selectedOptions).map(opt => opt.value);

    const inviteData = {
        name: formInviteUser.querySelector('#invite-user-name').value,
        email: formInviteUser.querySelector('#invite-user-email').value,
        roles: selectedRoles,
    };

    submitButton.disabled = true;
    submitButton.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Enviando...';

    fetch('/admin/api/users/invite', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(inviteData)
    })
    .then(res => res.json())
    .then(result => {
        if(result.success) {
            inviteUserModal.hide();
            alert(result.message); // Alerta simples por enquanto
            window.location.reload();
        } else {
            alertContainer.innerHTML = `<div class="alert alert-danger">${result.error}</div>`;
        }
    })
    .finally(() => {
        submitButton.disabled = false;
        submitButton.textContent = 'Enviar Convite';
    });
});