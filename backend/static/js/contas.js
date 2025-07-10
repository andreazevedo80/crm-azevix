document.addEventListener("DOMContentLoaded", function() {
    const displayArea = document.getElementById('contas-display-area');

    const renderContas = () => {
        fetch('/api/contas')
            .then(res => res.json())
            .then(data => {
                let tableContent = '';
                if (data.success && data.contas.length > 0) {
                    const rows = data.contas.map(conta => `
                        <tr>
                            <td>${conta.nome_fantasia}</td>
                            <td>${conta.cnpj || '-'}</td>
                            <td><span class="badge bg-secondary">${conta.tipo_conta}</span></td>
                            <td>${conta.owner_name}</td>
                            <td><a href="#" class="btn btn-sm btn-outline-primary disabled">Detalhes</a></td>
                        </tr>`).join('');
                    tableContent = `<div class="table-responsive"><table class="table table-hover"><thead><tr><th>Nome Fantasia</th><th>CNPJ</th><th>Tipo</th><th>Responsável</th><th>Ações</th></tr></thead><tbody>${rows}</tbody></table></div>`;
                } else {
                    tableContent = `<p class="text-center py-4">Nenhuma conta encontrada. <a href="#">Cadastre a primeira!</a></p>`;
                }
                displayArea.innerHTML = tableContent;
            })
            .catch(error => {
                console.error("Erro ao buscar contas:", error);
                displayArea.innerHTML = `<p class="text-center text-danger py-4">Ocorreu um erro ao carregar as contas.</p>`;
            });
    };

    renderContas();
});