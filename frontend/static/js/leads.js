document.addEventListener("DOMContentLoaded", () => {
    // 1. Popula os filtros primeiro
    populateFilters();
    // 2. Busca os leads iniciais
    fetchLeads();

    // 3. Adiciona listener ao formulário de edição para o botão salvar funcionar
    const editForm = document.getElementById("editForm");
    if (editForm) {
        editForm.addEventListener("submit", (e) => {
            e.preventDefault(); // Impede o recarregamento da página
            saveEdit();
        });
    }
});

let currentPage = 1;
const perPage = 10;

// FUNÇÃO NOVA: Busca as configs da API e preenche os filtros
function populateFilters() {
    fetch("/api/config")
        .then(res => res.json())
        .then(data => {
            if (!data.success) return;

            const statusFilter = document.getElementById("status-filter");
            const segmentFilter = document.getElementById("segment-filter");
            const editStatusSelect = document.getElementById("edit-status");
            const editSegmentoSelect = document.getElementById("edit-segmento");

            data.status_leads.forEach(status => {
                statusFilter.add(new Option(status, status));
                editStatusSelect.add(new Option(status, status));
            });

            data.segmentos.forEach(seg => {
                segmentFilter.add(new Option(seg, seg));
                editSegmentoSelect.add(new Option(seg, seg));
            });
        })
        .catch(error => console.error("Erro ao carregar configurações de filtro:", error));
}

function fetchLeads() {
    const search = document.getElementById("search").value;
    const status = document.getElementById("status-filter").value;
    const segmento = document.getElementById("segment-filter").value;
    const loadingDiv = document.getElementById("loading");
    const tableDiv = document.getElementById("leads-table-desktop");

    loadingDiv.style.display = "block"; // Mostra o spinner
    tableDiv.style.display = "none";  // Esconde a tabela

    const params = new URLSearchParams({ search, status, segmento, page: currentPage, per_page: perPage });

    fetch(`/api/leads?${params.toString()}`)
        .then(res => res.json())
        .then(data => {
            loadingDiv.style.display = "none"; // Esconde o spinner
            tableDiv.style.display = "block"; // Mostra a tabela

            const desktopList = document.getElementById("leads-list-desktop");
            const totalCounter = document.getElementById("total-count");
            desktopList.innerHTML = "";

            if (data.leads && data.leads.length > 0) {
                data.leads.forEach(lead => {
                    const row = document.createElement("tr");
                    row.innerHTML = `
                        <td>${lead.nome_completo}</td>
                        <td>${lead.nome_conta}</td>
                        <td>${lead.email || "-"}</td>
                        <td>${lead.telefone_celular || "-"}</td>
                        <td>${lead.segmento}</td>
                        <td><span class="badge bg-primary">${lead.status_lead}</span></td>
                        <td>${new Date(lead.data_ultima_atualizacao).toLocaleDateString()}</td>
                        <td>
                            <button class="btn btn-sm btn-primary me-1" onclick="openEditModal(${lead.id})"><i class="fas fa-edit"></i></button>
                            <button class="btn btn-sm btn-danger" onclick="deleteLead(${lead.id})"><i class="fas fa-trash"></i></button>
                        </td>`;
                    desktopList.appendChild(row);
                });
            } else {
                desktopList.innerHTML = `<tr><td colspan="8" class="text-center">Nenhum lead encontrado.</td></tr>`;
            }
            if (totalCounter) totalCounter.textContent = data.total;
        })
        .catch(error => {
            console.error("Erro ao buscar leads:", error);
            loadingDiv.style.display = "none";
            tableDiv.style.display = "block";
            document.getElementById("leads-list-desktop").innerHTML = `<tr><td colspan="8" class="text-center text-danger">Erro ao carregar dados.</td></tr>`;
        });
}

function applyFilters() {
    currentPage = 1;
    fetchLeads();
}

function openEditModal(id) {
    fetch(`/api/leads/${id}`)
        .then(res => res.json())
        .then(data => {
            if (!data.success) { alert("Erro ao carregar o lead."); return; }
            const lead = data.lead;
            document.getElementById("edit-id").value = lead.id;
            document.getElementById("edit-nome").value = lead.nome_completo;
            document.getElementById("edit-conta").value = lead.nome_conta;
            document.getElementById("edit-email").value = lead.email || "";
            document.getElementById("edit-telefone-fixo").value = lead.telefone_fixo || "";
            document.getElementById("edit-telefone-celular").value = lead.telefone_celular || "";
            document.getElementById("edit-segmento").value = lead.segmento;
            document.getElementById("edit-status").value = lead.status_lead;
            document.getElementById("edit-observacoes").value = lead.observacoes || "";
            
            const editModal = new bootstrap.Modal(document.getElementById('editModal'));
            editModal.show();
        });
}

function saveEdit() {
    const id = document.getElementById("edit-id").value;
    const leadData = {
        nome_completo: document.getElementById("edit-nome").value,
        nome_conta: document.getElementById("edit-conta").value,
        email: document.getElementById("edit-email").value,
        telefone_fixo: document.getElementById("edit-telefone-fixo").value,
        telefone_celular: document.getElementById("edit-telefone-celular").value,
        segmento: document.getElementById("edit-segmento").value,
        status_lead: document.getElementById("edit-status").value,
        observacoes: document.getElementById("edit-observacoes").value,
    };

    fetch(`/api/leads/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(leadData),
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            const editModalEl = document.getElementById('editModal');
            const modal = bootstrap.Modal.getInstance(editModalEl);
            modal.hide();
            fetchLeads();
        } else {
            alert("Erro ao salvar: " + (data.error || "Erro desconhecido."));
        }
    });
}

function deleteLead(id) {
    if (confirm("Tem certeza que deseja excluir este lead?")) {
        fetch(`/api/leads/${id}`, { method: "DELETE" })
        .then(() => fetchLeads());
    }
}