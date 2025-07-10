document.addEventListener("DOMContentLoaded", function () {
  // Make table rows clickable, except elements marked with .no-click
  document.querySelectorAll(".clickable-row").forEach((row) => {
    row.addEventListener("click", (event) => {
      if (event.target.closest(".no-click")) return;
      window.location = row.dataset.href;
    });
  });

  // Delete All Adjustments modal logic
  const confirmDeleteAllBtn = document.getElementById(
    "confirmDeleteAllAdjustmentsBtn",
  );
  const deleteAllForm = document.getElementById("deleteAllAdjustmentsForm");

  if (confirmDeleteAllBtn && deleteAllForm) {
    confirmDeleteAllBtn.addEventListener("click", function () {
      deleteAllForm.submit();
    });
  }
});
