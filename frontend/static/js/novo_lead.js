// frontend/static/js/novo_lead.js

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("leadForm");
  const alertContainer = document.getElementById("alert-container");
  const segmentoSelect = document.getElementById("segmento");

  // Preenche opções de segmento
  fetch("/api/config")
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        data.segmentos.forEach(seg => {
          const opt = document.createElement("option");
          opt.value = seg;
          opt.textContent = seg;
          segmentoSelect.appendChild(opt);
        });
      }
    });

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const formData = new FormData(form);
    const leadData = {};

    for (let [key, value] of formData.entries()) {
      leadData[key] = value;
    }

    fetch("/api/leads", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(leadData)
    })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          showAlert("Lead cadastrado com sucesso!", "success");
          form.reset();
        } else {
          showAlert(data.error || "Erro ao cadastrar lead.", "danger");
        }
      })
      .catch(() => showAlert("Erro na requisição.", "danger"));
  });

  function showAlert(message, type) {
    alertContainer.innerHTML = `
      <div class="alert alert-${type} alert-dismissible fade show" role="alert">
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
      </div>`;
  }
});