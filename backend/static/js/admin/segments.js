document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('segment-form');
    const formTitle = document.getElementById('form-title-sg');
    const segmentIdInput = document.getElementById('sg-id');
    const segmentNomeInput = document.getElementById('sg-nome');
    const cancelBtn = document.getElementById('cancel-btn-sg');
    const tableBody = document.getElementById('segments-table-body');
    const applyDefaultsBtn = document.getElementById('apply-defaults-btn-sg');

    let currentSegments = [];

    const renderTable = () => {
        tableBody.innerHTML = '';
        currentSegments.forEach(segment => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${segment.nome}</td>
                <td>
                    <span class="badge bg-${segment.is_active ? 'success' : 'danger'}">
                        ${segment.is_active ? 'Ativo' : 'Inativo'}
                    </span>
                </td>
                <td>
                    <button class="btn btn-sm btn-outline-secondary" onclick="handleEdit(${segment.id})"><i class="fas fa-pencil-alt"></i></button>
                    <button class="btn btn-sm btn-outline-${segment.is_active ? 'danger' : 'success'}" onclick="handleToggleActive(${segment.id}, ${!segment.is_active})">
                        <i class="fas ${segment.is_active ? 'fa-toggle-off' : 'fa-toggle-on'}"></i>
                    </button>
                </td>
            `;
            tableBody.appendChild(row);
        });
    };

    const fetchSegments = () => {
        fetch('/admin/api/segments')
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    currentSegments = data.segments;
                    renderTable();
                }
            });
    };
    
    const resetForm = () => {
        form.reset();
        segmentIdInput.value = '';
        formTitle.textContent = 'Adicionar Novo Segmento';
        cancelBtn.style.display = 'none';
    };

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const id = segmentIdInput.value;
        const nome = segmentNomeInput.value;
        
        const url = id ? `/admin/api/segments/${id}` : '/admin/api/segments';
        const method = id ? 'PUT' : 'POST';

        fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ nome: nome })
        })
        .then(res => res.json())
        .then(data => {
            if(data.success) {
                fetchSegments();
                resetForm();
            } else {
                alert(`Erro: ${data.error}`);
            }
        });
    });

    window.handleEdit = (id) => {
        const segment = currentSegments.find(s => s.id === id);
        if (segment) {
            formTitle.textContent = 'Editar Segmento';
            segmentIdInput.value = segment.id;
            segmentNomeInput.value = segment.nome;
            cancelBtn.style.display = 'inline-block';
        }
    };
    
    window.handleToggleActive = (id, newStatus) => {
        const segment = currentSegments.find(s => s.id === id);
        fetch(`/admin/api/segments/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ is_active: newStatus, nome: segment.nome })
        })
        .then(res => res.json())
        .then(data => {
            if(data.success) {
                fetchSegments();
            }
        });
    };

    cancelBtn.addEventListener('click', resetForm);

    // --- ADIÇÃO v9.3: Listener para o botão de aplicar padrão ---
    applyDefaultsBtn.addEventListener('click', () => {
        if (confirm('Isso adicionará os segmentos de mercado padrão do sistema que ainda não existirem. Deseja continuar?')) {
            fetch('/admin/api/segments/apply-defaults', { method: 'POST' })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        alert(data.message);
                        fetchSegments(); // Recarrega a tabela
                    } else {
                        alert(`Erro: ${data.error}`);
                    }
                });
        }
    });


    fetchSegments();
});