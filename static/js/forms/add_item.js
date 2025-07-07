document.addEventListener("DOMContentLoaded", function () {
  const checkbox = document.getElementById("id_track_inventory");
  const inventoryFieldsContainer = document.getElementById(
    "inventoryFieldsContainer",
  );

  function toggleInventoryFields() {
    const isChecked = checkbox.checked;
    if (isChecked) {
      inventoryFieldsContainer.classList.remove("d-none");
    } else {
      inventoryFieldsContainer.classList.add("d-none");
    }
  }

  if (checkbox && inventoryFieldsContainer) {
    toggleInventoryFields(); // Set initial state
    checkbox.addEventListener("change", toggleInventoryFields);
  }

  const imageInput = document.getElementById("id_image");
  const preview = document.getElementById("imagePreview");
  const previewWrapper = document.getElementById("imagePreviewWrapper");
  const placeholder = document.getElementById("imagePlaceholder");

  imageInput.addEventListener("change", function () {
    const file = this.files[0];
    if (file && file.type.startsWith("image/")) {
      const reader = new FileReader();
      reader.onload = function (e) {
        preview.src = e.target.result;
        preview.classList.remove("d-none");
        previewWrapper.classList.remove("d-none");
        placeholder.classList.add("d-none");
      };
      reader.readAsDataURL(file);
    }
  });

  window.clearImage = function (e) {
    e.stopPropagation(); // prevent click from opening file dialog
    imageInput.value = ""; // clear file input
    previewWrapper.classList.add("d-none");
    placeholder.classList.remove("d-none");
  };
});
