// frontend/static/js/leads.js

document.addEventListener("DOMContentLoaded", () => {
  // Funções para popular os filtros são chamadas primeiro
  populateFilters();

  // A busca inicial de leads é feita depois que os filtros estão prontos
  fetchLeads();

  // Adiciona o listener para o formulário de edição
  const editForm = document.getElementById("editForm");
  if (editForm) {
    editForm.addEventListener("submit", (e) => {
      e.preventDefault();
      saveEdit();
    });
  }
});

let currentPage = 1;
const perPage = 10;

/**
 * Busca as opções de Segmento e Status da API e preenche os selects.
 */
function populateFilters() {
  fetch("/api/config")
    .then(res => res.json())
    .then(data => {
      if (!data.success) return;

      const statusFilter = document.getElementById("status-filter");
      const segmentFilter = document.getElementById("segment-filter");
      const editStatus = document.getElementById("edit-status");
      const editSegmento = document.getElementById("edit-segmento");

      // Limpa opções existentes (exceto a primeira "Todos")
      const clearOptions = (select) => {
        while (select.options.length > 1) {
          select.remove(1);
        }
      };
      
      clearOptions(statusFilter);
      clearOptions(segmentFilter);
      clearOptions(editStatus);
      clearOptions(editSegmento);

      // Popula Status
      data.status_leads.forEach(status => {
        statusFilter.appendChild(new Option(status, status));
        editStatus.appendChild(new Option(status, status));
      });

      // Popula Segmentos
      data.segmentos.forEach(seg => {
        segmentFilter.appendChild(new Option(seg, seg));
        editSegmento.appendChild(new Option(seg, seg));
      });
    })
    .catch(error => console.error("Erro ao popular filtros:", error));
}


/**
 * Busca os leads da API e atualiza a tabela.
 */
function fetchLeads() {
  const search = document.getElementById("search").value;
  const status = document.getElementById("status-filter").value;
  const segmento = document.getElementById("segment-filter").value;
  const loading = document.getElementById("loading");
  const desktopTable = document.getElementById("leads-table-desktop");

  if (loading) loading.style.display = "block";
  if (desktopTable) desktopTable.style.display = "none";

  const params = new URLSearchParams({
    search,
    status,
    segmento,
    page: currentPage,
    per_page: perPage,
  });

  fetch(`/api/leads?${params.toString()}`)
    .then(res => res.json())
    .then(data => {
      if (loading) loading.style.display = "none";
      if (desktopTable) desktopTable.style.display = "block";

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
              <button class="btn btn-sm btn-primary me-1" onclick="openEditModal(${lead.id})">
                <i class="fas fa-edit"></i>
              </button>
              <button class="btn btn-sm btn-danger" onclick="deleteLead(${lead.id})">
                <i class="fas fa-trash"></i>
              </button>
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
      if (loading) loading.style.display = "none";
      const desktopList = document.getElementById("leads-list-desktop");
      desktopList.innerHTML = `<tr><td colspan="8" class="text-center text-danger">Erro ao carregar os leads. Verifique a console.</td></tr>`;
    });
}

function applyFilters() {
  currentPage = 1;
  fetchLeads();
}

/**
 * Busca dados de um lead e abre o modal de edição.
 */
function openEditModal(id) {
  fetch(`/api/leads/${id}`)
    .then(res => res.json())
    .then(data => {
      if (!data.success) {
        alert("Erro ao carregar dados do lead.");
        return;
      }
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

      new bootstrap.Modal(document.getElementById("editModal")).show();
    });
}

/**
 * Salva as alterações do formulário de edição.
 */
function saveEdit() {
  const id = document.getElementById("edit-id").value;
  const data = {
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
    body: JSON.stringify(data),
  })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        const modalElement = document.getElementById("editModal");
        const modalInstance = bootstrap.Modal.getInstance(modalElement);
        modalInstance.hide();
        fetchLeads(); // Atualiza a lista
      } else {
        alert("Erro ao salvar: " + data.error);
      }
    });
}

/**
 * Deleta um lead após confirmação.
 */
function deleteLead(id) {
  if (confirm("Deseja realmente excluir este lead?")) {
    fetch(`/api/leads/${id}`, {
      method: "DELETE",
    })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          fetchLeads(); // Atualiza a lista
        } else {
          alert("Erro ao excluir: " + data.error);
        }
      });
  }
}