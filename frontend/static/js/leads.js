// frontend/static/js/leads.js

let currentPage = 1;
const perPage = 10;

function fetchLeads() {
  const search = document.getElementById("search").value;
  const status = document.getElementById("status-filter").value;
  const segmento = document.getElementById("segment-filter").value;

  const params = new URLSearchParams({
    search,
    status,
    segmento,
    page: currentPage,
    per_page: perPage
  });

  fetch(`/api/leads?${params.toString()}`)
    .then(res => res.json())
    .then(data => {
      const desktopList = document.getElementById("leads-list-desktop");
      const totalCounter = document.getElementById("total-count");

      desktopList.innerHTML = "";
      data.leads.forEach(lead => {
        const row = document.createElement("tr");
        row.innerHTML = `
          <td>${lead.nome_completo}</td>
          <td>${lead.nome_conta}</td>
          <td>${lead.email}</td>
          <td>${lead.telefone_celular || "-"}</td>
          <td>${lead.segmento}</td>
          <td>${lead.status_lead}</td>
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

      if (totalCounter) totalCounter.textContent = data.total;
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
      const lead = data.lead;
      document.getElementById("edit-id").value = lead.id;
      document.getElementById("edit-nome").value = lead.nome_completo;
      document.getElementById("edit-conta").value = lead.nome_conta;
      document.getElementById("edit-email").value = lead.email;
      document.getElementById("edit-telefone-fixo").value = lead.telefone_fixo || "";
      document.getElementById("edit-telefone-celular").value = lead.telefone_celular || "";
      document.getElementById("edit-segmento").value = lead.segmento;
      document.getElementById("edit-status").value = lead.status_lead;
      document.getElementById("edit-observacoes").value = lead.observacoes || "";
      new bootstrap.Modal(document.getElementById("editModal")).show();
    });
}

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
    observacoes: document.getElementById("edit-observacoes").value
  };

  fetch(`/api/leads/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  }).then(() => {
    bootstrap.Modal.getInstance(document.getElementById("editModal")).hide();
    fetchLeads();
  });
}

function deleteLead(id) {
  if (!confirm("Deseja realmente excluir este lead?")) return;

  fetch(`/api/leads/${id}`, {
    method: "DELETE"
  }).then(() => fetchLeads());
}

document.addEventListener("DOMContentLoaded", () => {
  fetchLeads();
});