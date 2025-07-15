document.addEventListener("DOMContentLoaded", function () {
  const canvas = document.getElementById("stockChart");
  if (!canvas) return;

  const ctx = canvas.getContext("2d");

  new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: ["Sufficient Stock", "Low Stock"],
      datasets: [
        {
          data: [sufficientStockCount, lowStockCount],
          backgroundColor: ["#28a745", "#dc3545"],
          borderWidth: 1,
          borderRadius: 2,
          spacing: 2,
          hoverOffset: 4,
        },
      ],
    },
    options: {
      cutout: "70%",
      plugins: {
        legend: {
          display: true,
          position: "bottom",
          labels: {
            usePointStyle: true,
            pointStyle: "circle",
            boxWidth: 20,
            padding: 15,
            font: {
              size: 10,
            },
          },
        },
        tooltip: {
          callbacks: {
            label: function (context) {
              const label = context.label || "";
              const value = context.raw || 0;
              return `${label}: ${value}`;
            },
          },
        },
      },
    },
  });
});
