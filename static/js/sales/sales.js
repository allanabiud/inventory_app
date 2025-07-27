document.addEventListener("DOMContentLoaded", function () {
  // Handle row click navigation
  document.querySelectorAll(".clickable-row").forEach((row) => {
    row.addEventListener("click", (event) => {
      // Prevent navigation if clicked element or parent has class 'no-click'
      if (event.target.closest(".no-click")) return;

      const href = row.dataset.href;
      if (href) {
        window.location = href;
      }
    });
  });

  // Handle "Delete All" confirmation modal action
  const confirmDeleteAllBtn = document.getElementById("confirmDeleteAllBtn");
  const deleteAllSalesForm = document.getElementById("deleteAllSalesForm");

  if (confirmDeleteAllBtn && deleteAllSalesForm) {
    confirmDeleteAllBtn.addEventListener("click", function () {
      deleteAllSalesForm.submit();
    });
  }
});
