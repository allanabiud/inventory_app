document.addEventListener("DOMContentLoaded", function () {
  const monthlyCanvas = document.getElementById("monthly-sales-chart");
  if (monthlyCanvas) {
    const ctx = document.getElementById("monthly-sales-chart").getContext("2d");
    const currentMonth = new Date().toLocaleString("default", {
      month: "long",
    });
    const rawDates = monthlyData.rawDates;
    new Chart(ctx, {
      type: "bar",
      data: {
        labels: monthlyData.labels,
        datasets: [
          {
            ...monthlyData.datasets[0],
            backgroundColor: "#a7288a",
            borderRadius: 3,
            barPercentage: 0.5,
            categoryPercentage: 0.9,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: {
          duration: 800,
          easing: "easeOutQuart",
        },
        scales: {
          x: {
            title: {
              display: true,
              text: currentMonth,
              color: "#6c757d",
              font: { size: 13, weight: "bold" },
            },
            ticks: {
              autoSkip: false,
              maxRotation: 0,
              minRotation: 0,
            },
            grid: {
              display: false,
            },
          },
          y: {
            title: {
              display: true,
              text: "KES",
              color: "#6c757d",
              font: { size: 13, weight: "bold" },
            },
            beginAtZero: true,
            ticks: {
              callback: (value) =>
                new Intl.NumberFormat("en-KE", {
                  style: "currency",
                  currency: "KES",
                  minimumFractionDigits: 0,
                }).format(value),
            },
            grid: {
              color: "#6c757d",
            },
          },
        },
        plugins: {
          legend: {
            position: "top",
          },
          tooltip: {
            callbacks: {
              title: (tooltipItems) => {
                const index = tooltipItems[0].dataIndex;
                const date = new Date(rawDates[index]);
                const day = date.getDate();
                const month = date.toLocaleString("default", { month: "long" });
                return `${month} ${day}`;
              },

              label: (context) => {
                const value = context.raw;
                return new Intl.NumberFormat("en-KE", {
                  style: "currency",
                  currency: "KES",
                  minimumFractionDigits: 0,
                }).format(value);
              },
            },
            borderColor: "#a7288a",
            borderWidth: 1,
          },
        },
      },
    });
  }

  const yearlyCanvas = document.getElementById("yearly-sales-chart");
  if (yearlyCanvas) {
    const ctx = yearlyCanvas.getContext("2d");
    new Chart(ctx, {
      type: "bar",
      data: yearlyData, // assuming this is defined
      options: {},
    });
  }
});
