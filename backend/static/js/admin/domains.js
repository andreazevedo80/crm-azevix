document.addEventListener('DOMContentLoaded', function() {
    const domainList = document.getElementById('domain-list');
    const addDomainForm = document.getElementById('addDomainForm');
    const domainInput = document.getElementById('domain-name');

    const renderDomains = (domains) => {
        domainList.innerHTML = '';
        if (domains.length > 0) {
            domains.forEach(d => {
                const li = document.createElement('li');
                li.className = 'list-group-item d-flex justify-content-between align-items-center';
                li.textContent = `@${d.domain}`;
                
                const deleteBtn = document.createElement('button');
                deleteBtn.className = 'btn btn-sm btn-outline-danger';
                deleteBtn.innerHTML = '<i class="fas fa-trash"></i>';
                deleteBtn.onclick = () => handleDelete(d.id);
                
                li.appendChild(deleteBtn);
                domainList.appendChild(li);
            });
        } else {
            domainList.innerHTML = '<li class="list-group-item text-center text-muted">Nenhum domínio cadastrado. Todos os e-mails são permitidos.</li>';
        }
    };

    const fetchDomains = () => {
        fetch('/admin/api/domains')
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    renderDomains(data.domains);
                }
            });
    };

    const handleDelete = (domainId) => {
        if (confirm('Tem certeza que deseja remover este domínio?')) {
            fetch(`/admin/api/domains/${domainId}`, { method: 'DELETE' })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        fetchDomains();
                    } else {
                        alert(`Erro: ${data.error}`);
                    }
                });
        }
    };

    addDomainForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const domainName = domainInput.value.trim();
        if (!domainName) return;

        fetch('/admin/api/domains', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ domain: domainName })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                domainInput.value = '';
                fetchDomains();
            } else {
                alert(`Erro: ${data.error}`);
            }
        });
    });

    fetchDomains();
});