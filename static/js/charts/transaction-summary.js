document.addEventListener("DOMContentLoaded", function () {
  const purchasesColor = "#6610F2";
  const salesColor = "#A7288A";
  const mutedTextColor = "#6c757d";

  const monthlyChartData = JSON.parse(
    document.getElementById("monthly-chart-data").textContent,
  );
  const yearlyChartData = JSON.parse(
    document.getElementById("yearly-chart-data").textContent,
  );
  const initialFilter = initialChartFilter;

  let monthlyChartInstance = null;
  let yearlyChartInstance = null;

  function createOrUpdateChart(canvasId, chartData, period) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;
    const ctx = canvas.getContext("2d");

    let existingChart = Chart.getChart(canvasId);
    if (existingChart) {
      existingChart.destroy();
    }

    const chartTitle =
      period === "month"
        ? `Daily Transactions (${new Date().toLocaleString("default", { month: "long" })})`
        : `Monthly Transactions (${new Date().getFullYear()})`;

    const tooltipTitleCallback = (tooltipItems) => {
      const index = tooltipItems[0].dataIndex;
      const rawDateStr = chartData.rawDates[index];
      if (!rawDateStr) return "";

      const date = new Date(rawDateStr);
      if (period === "month") {
        const day = date.getDate();
        const month = date.toLocaleString("default", { month: "long" });
        const year = date.getFullYear();
        return `${month} ${day}, ${year}`;
      } else {
        const month = date.toLocaleString("default", { month: "long" });
        const year = date.getFullYear();
        return `${month}, ${year}`;
      }
    };

    return new Chart(ctx, {
      type: "bar",
      data: {
        labels: chartData.labels,
        datasets: [
          {
            label: "Purchases",
            data: chartData.datasets[1].data,
            backgroundColor: purchasesColor,
            borderColor: purchasesColor,
            borderWidth: 1,
            borderRadius: 5,
            barPercentage: 0.7,
            categoryPercentage: 0.8,
            hoverBackgroundColor: "rgba(102, 16, 242, 0.8)",
            hoverBorderColor: purchasesColor,
          },
          {
            label: "Sales",
            data: chartData.datasets[0].data,
            backgroundColor: salesColor,
            borderColor: salesColor,
            borderWidth: 1,
            borderRadius: 5,
            barPercentage: 0.7,
            categoryPercentage: 0.8,
            hoverBackgroundColor: "rgba(167, 40, 138, 0.8)",
            hoverBorderColor: salesColor,
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
        plugins: {
          legend: {
            position: "top",
            labels: {
              font: {
                size: 14,
                weight: "bold",
              },
              color: mutedTextColor,
              usePointStyle: true,
              pointStyle: "rectRounded",
              borderRadius: 3,
            },
          },
          tooltip: {
            backgroundColor: "rgba(0, 0, 0, 0.75)",
            titleFont: {
              size: 12,
              weight: "bold",
            },
            bodyFont: {
              size: 12,
            },
            padding: 10,
            displayColors: true,
            borderColor: (tooltipContext) => {
              if (tooltipContext.tooltip.dataPoints.length > 0) {
                const datasetLabel =
                  tooltipContext.tooltip.dataPoints[0].dataset.label;
                if (datasetLabel === "Sales") {
                  return salesColor;
                } else if (datasetLabel === "Purchases") {
                  return purchasesColor;
                }
              }
              return "#ced4da"; // Fallback color
            },
            borderWidth: 1,
            cornerRadius: 6,
            callbacks: {
              title: tooltipTitleCallback,
              label: (context) => {
                const label = context.dataset.label || "";
                const value = context.raw;
                return (
                  `${label}: ` +
                  new Intl.NumberFormat("en-KE", {
                    style: "currency",
                    currency: "KES",
                    minimumFractionDigits: 0,
                    maximumFractionDigits: 2,
                  }).format(value)
                );
              },
            },
          },
        },
        scales: {
          x: {
            stacked: false,
            title: {
              display: true,
              text: chartTitle,
              color: mutedTextColor,
              font: { size: 14, weight: "bold" },
            },
            ticks: {
              autoSkip: false,
              maxRotation: 45,
              minRotation: 0,
              color: mutedTextColor,
            },
            grid: {
              display: false,
            },
          },
          y: {
            stacked: false,
            title: {
              display: true,
              text: "Amount (KES)",
              color: mutedTextColor,
              font: { size: 14, weight: "bold" },
            },
            beginAtZero: true,
            ticks: {
              color: mutedTextColor,
              callback: (value) =>
                new Intl.NumberFormat("en-KE", {
                  style: "decimal",
                  minimumFractionDigits: 0,
                  maximumFractionDigits: 0,
                }).format(value),
            },
            grid: {
              color: "#dee2e6",
              borderDash: [2, 2],
              drawBorder: false,
            },
          },
        },
      },
    });
  }

  if (initialFilter === "month") {
    monthlyChartInstance = createOrUpdateChart(
      "monthly-sales-chart",
      monthlyChartData,
      "month",
    );
    document.getElementById("monthly-sales-chart").style.display = "block";
    document.getElementById("yearly-sales-chart").style.display = "none";
  } else if (initialFilter === "year") {
    yearlyChartInstance = createOrUpdateChart(
      "yearly-sales-chart",
      yearlyChartData,
      "year",
    );
    document.getElementById("monthly-sales-chart").style.display = "none";
    document.getElementById("yearly-sales-chart").style.display = "block";
  }

  document.querySelectorAll(".time-filter-option").forEach((option) => {
    option.addEventListener("click", function (e) {
      e.preventDefault();
      const selectedFilter = this.dataset.filter;

      // Update dropdown button label
      document.getElementById("timeFilterBtn").textContent =
        selectedFilter === "year" ? "This Year" : "This Month";

      // Swap chart
      if (selectedFilter === "month") {
        monthlyChartInstance = createOrUpdateChart(
          "monthly-sales-chart",
          monthlyChartData,
          "month",
        );
        document.getElementById("monthly-sales-chart").style.display = "block";
        document.getElementById("yearly-sales-chart").style.display = "none";
      } else if (selectedFilter === "year") {
        yearlyChartInstance = createOrUpdateChart(
          "yearly-sales-chart",
          yearlyChartData,
          "year",
        );
        document.getElementById("monthly-sales-chart").style.display = "none";
        document.getElementById("yearly-sales-chart").style.display = "block";
      }

      // Update active class
      document
        .querySelectorAll(".time-filter-option")
        .forEach((el) => el.classList.remove("active"));
      this.classList.add("active");
    });
  });
});
