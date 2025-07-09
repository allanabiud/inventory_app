document.addEventListener("DOMContentLoaded", function () {
  const imageInput = document.getElementById("id_image");
  const imagePreview = document.getElementById("imagePreview");
  const imagePreviewWrapper = document.getElementById("imagePreviewWrapper");
  const imagePlaceholder = document.getElementById("imagePlaceholder");
  const clearImageBtn = document.getElementById("clearImageBtn");
  const clearImageHiddenInput = document.getElementById("id_clear_image"); // SKU prefix and number fields

  const skuPrefixInput = document.getElementById("id_sku_prefix");
  const skuNumberInput = document.getElementById("id_sku_number");
  const skuHiddenInput = document.getElementById("id_sku"); // --- Removed: Inventory Toggling Logic ---
  function updateImagePreview(file) {
    if (file) {
      const reader = new FileReader();
      reader.onload = function (e) {
        imagePreview.src = e.target.result;
        imagePreview.classList.remove("d-none");
        imagePreviewWrapper.classList.remove("d-none");
        imagePlaceholder.classList.add("d-none");
        clearImageHiddenInput.value = "false"; // New image selected, don't clear on save
      };
      reader.readAsDataURL(file);
    } else {
      // No file selected (e.g., clear button pressed or initial load with no image)
      imagePreview.src = "#";
      imagePreview.classList.add("d-none"); // Hide the img element
      imagePreviewWrapper.classList.add("d-none"); // Hide the container as well
      imagePlaceholder.classList.remove("d-none"); // Show the placeholder
      clearImageHiddenInput.value = "true"; // Signal for server to clear image
    }
  }

  imageInput.addEventListener("change", function () {
    updateImagePreview(this.files[0]);
  }); // Clear Image Button Functionality

  clearImageBtn.addEventListener("click", function (event) {
    event.stopPropagation(); // Prevent click from bubbling to imageUploadContainer
    imageInput.value = ""; // Clear the file input
    updateImagePreview(null); // Reset preview to placeholder and set hidden input
  }); // Initial check for existing image on page load (for edit form)
  // If imagePreview.src is not empty and not just '#', assume an image is present

  if (imagePreview.src && imagePreview.src !== window.location.href + "#") {
    imagePreview.classList.remove("d-none");
    imagePreviewWrapper.classList.remove("d-none");
    imagePlaceholder.classList.add("d-none");
  } else {
    // No image currently loaded
    imagePreview.classList.add("d-none");
    imagePreviewWrapper.classList.add("d-none");
    imagePlaceholder.classList.remove("d-none");
  } // --- SKU Concatenation Logic (Remains the same as it's already correct) ---

  function updateSkuHiddenInput() {
    const prefix = skuPrefixInput.value.trim();
    const number = skuNumberInput.value.trim();
    if (prefix && number) {
      skuHiddenInput.value = `${prefix}-${number}`;
    } else if (prefix) {
      skuHiddenInput.value = prefix; // Allow just a prefix
    } else {
      skuHiddenInput.value = ""; // Clear SKU if both are empty
    }
  }

  skuPrefixInput.addEventListener("input", updateSkuHiddenInput);
  skuNumberInput.addEventListener("input", updateSkuHiddenInput); // Initial SKU update on page load for existing items

  updateSkuHiddenInput();
});

// Global function for the image container click (if you prefer inline onclick)
// This function is still needed if you have `onclick="document.getElementById('id_image').click();"`
// on `imageUploadContainer` and `onclick="clearImage(event)"` on `clearImageBtn`.
// The event listener on clearImageBtn is the preferred way, but keeping this if inline is used.
function clearImage(event) {
  event.stopPropagation(); // Prevent click from bubbling to imageUploadContainer
  const imageInput = document.getElementById("id_image");
  const imagePreview = document.getElementById("imagePreview");
  const imagePreviewWrapper = document.getElementById("imagePreviewWrapper");
  const imagePlaceholder = document.getElementById("imagePlaceholder");
  const clearImageHiddenInput = document.getElementById("id_clear_image");

  imageInput.value = ""; // Clear the file input
  imagePreview.src = "#";
  imagePreview.classList.add("d-none");
  imagePreviewWrapper.classList.add("d-none");
  imagePlaceholder.classList.remove("d-none");
  clearImageHiddenInput.value = "true"; // Signal to delete on save
}
