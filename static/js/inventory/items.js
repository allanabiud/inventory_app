document.addEventListener("DOMContentLoaded", function () {
  // Existing clickable row logic
  document.querySelectorAll(".clickable-row").forEach((row) => {
    row.addEventListener("click", (event) => {
      // Ignore clicks on any element inside a cell marked no-click
      if (event.target.closest(".no-click")) return;

      window.location = row.dataset.href;
    });
  });

  // Logic for Delete All Confirmation Modal
  // Get the button inside the modal that confirms deletion
  const confirmDeleteAllBtn = document.getElementById("confirmDeleteAllBtn");
  // Get the form that will actually perform the deletion
  const deleteAllItemsForm = document.getElementById("deleteAllItemsForm");

  if (confirmDeleteAllBtn && deleteAllItemsForm) {
    confirmDeleteAllBtn.addEventListener("click", function () {
      deleteAllItemsForm.submit();
    });
  }
});
