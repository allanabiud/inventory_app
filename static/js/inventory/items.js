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
    confirmDeleteAllBtn.addEventListener("click", function (event) {
      // Prevent the button's default submit action (which is already type="submit" in the form)
      // and instead, explicitly submit the form. This is a bit redundant if the button is type="submit"
      // within the form, but ensures the form is submitted correctly.
      // If the button was outside the form, this would be crucial.
      // Since it's inside, a simple type="submit" is enough, but this is harmless.
      deleteAllItemsForm.submit();
    });
  }
});
