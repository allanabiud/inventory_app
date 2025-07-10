document.addEventListener("DOMContentLoaded", function () {
  // Make table rows clickable
  document.querySelectorAll(".clickable-row").forEach((row) => {
    row.addEventListener("click", (event) => {
      if (event.target.closest(".no-click")) return;
      window.location = row.dataset.href;
    });
  });

  // Delete all modal logic
  const confirmDeleteAllBtn = document.getElementById(
    "confirmDeleteAllUnitsBtn",
  );
  const deleteAllUnitsForm = document.getElementById("deleteAllUnitsForm");

  if (confirmDeleteAllBtn && deleteAllUnitsForm) {
    confirmDeleteAllBtn.addEventListener("click", function () {
      deleteAllUnitsForm.submit();
    });
  }
});
