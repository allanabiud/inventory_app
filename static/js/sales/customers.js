document.addEventListener("DOMContentLoaded", function () {
  // Clickable row navigation
  document.querySelectorAll(".clickable-row").forEach((row) => {
    row.addEventListener("click", (event) => {
      if (event.target.closest(".no-click")) return;
      const href = row.dataset.href;
      if (href) {
        window.location = href;
      }
    });
  });

  // Confirm delete all customers
  const confirmDeleteAllBtn = document.getElementById(
    "confirmDeleteAllCustomersBtn",
  );
  const deleteAllCustomersForm = document.getElementById(
    "deleteAllCustomersForm",
  );

  if (confirmDeleteAllBtn && deleteAllCustomersForm) {
    confirmDeleteAllBtn.addEventListener("click", function () {
      deleteAllCustomersForm.submit();
    });
  }
});
