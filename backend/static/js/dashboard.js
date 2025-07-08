// frontend/static/js/dashboard.js
// Preenche dashboard com dados da API

document.addEventListener("DOMContentLoaded", function () {
  fetch("/api/dashboard/stats")
    .then((res) => res.json())
    .then((data) => {
      if (!data.success) return;

      // Total de leads
      const counter = document.getElementById("total-count");
      if (counter) counter.textContent = data.total_leads;

      // Gráfico por status
      const statusChartCtx = document.getElementById("statusChart");
      if (statusChartCtx) {
        new Chart(statusChartCtx, {
          type: "pie",
          data: {
            labels: Object.keys(data.status_stats),
            datasets: [{
              data: Object.values(data.status_stats),
              backgroundColor: ["#007bff", "#28a745", "#ffc107", "#dc3545", "#6c757d", "#20c997", "#fd7e14"]
            }]
          }
        });
      }

      // Gráfico por segmento
      const segmentChartCtx = document.getElementById("segmentChart");
      if (segmentChartCtx) {
        new Chart(segmentChartCtx, {
          type: "bar",
          data: {
            labels: Object.keys(data.segment_stats),
            datasets: [{
              label: "Leads",
              data: Object.values(data.segment_stats),
              backgroundColor: "#17a2b8"
            }]
          },
          options: {
            indexAxis: 'y'
          }
        });
      }

      // Lista de leads recentes
      const tbody = document.getElementById("recent-leads");
      if (tbody) {
        data.recent_leads.forEach((lead) => {
          const row = document.createElement("tr");
          row.innerHTML = `
            <td>${lead.nome_completo}</td>
            <td>${lead.nome_conta}</td>
            <td>${lead.segmento}</td>
            <td>${lead.status_lead}</td>
            <td>${new Date(lead.data_cadastro).toLocaleDateString()}</td>`;
          tbody.appendChild(row);
        });
      }
    })
    .catch(console.error);
});
