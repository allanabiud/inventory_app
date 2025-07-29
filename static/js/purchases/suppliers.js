document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".clickable-row").forEach((row) => {
    row.addEventListener("click", (event) => {
      if (event.target.closest(".no-click")) return;
      const href = row.dataset.href;
      if (href) {
        window.location = href;
      }
    });
  });

  const confirmDeleteAllBtn = document.getElementById(
    "confirmDeleteAllSuppliersBtn",
  );
  const deleteAllSuppliersForm = document.getElementById(
    "deleteAllSuppliersForm",
  );

  if (confirmDeleteAllBtn && deleteAllSuppliersForm) {
    confirmDeleteAllBtn.addEventListener("click", function () {
      deleteAllSuppliersForm.submit();
    });
  }
});
