document.addEventListener("DOMContentLoaded", function () {
  // Make table rows clickable
  document.querySelectorAll(".clickable-row").forEach((row) => {
    row.addEventListener("click", (event) => {
      if (event.target.closest(".no-click")) return;
      window.location = row.dataset.href;
    });
  });

  // Delete all modal logic
  const confirmDeleteAllBtn = document.getElementById("confirmDeleteAllBtn");
  const deleteAllCategoriesForm = document.getElementById(
    "deleteAllCategoriesForm",
  );

  if (confirmDeleteAllBtn && deleteAllCategoriesForm) {
    confirmDeleteAllBtn.addEventListener("click", function () {
      deleteAllCategoriesForm.submit();
    });
  }
});
