document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".clickable-row").forEach((row) => {
    row.addEventListener("click", (event) => {
      // Ignore clicks on any element inside a cell marked no-click
      if (event.target.closest(".no-click")) return;

      window.location = row.dataset.href;
    });
  });
});
