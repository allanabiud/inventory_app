document.addEventListener("DOMContentLoaded", function () {
  // --- SKU Combination Logic (remains, as HTML uses prefix/number inputs) ---
  const skuPrefixInput = document.getElementById("id_sku_prefix");
  const skuNumberInput = document.getElementById("id_sku_number");
  const hiddenSkuInput = document.getElementById("id_sku");
  const itemForm = document.getElementById("itemForm");

  /**
   * Combines the SKU prefix and number into a single SKU string
   * and updates the hidden SKU input field.
   */
  function combineSku() {
    const prefix = skuPrefixInput.value.trim();
    const number = skuNumberInput.value.trim();
    let combinedSku = "";

    if (prefix && number) {
      combinedSku = `${prefix}-${number}`;
    } else if (prefix) {
      combinedSku = prefix;
    } else if (number) {
      combinedSku = number;
    }
    // If both are empty, combinedSku remains an empty string, which the server will validate.

    hiddenSkuInput.value = combinedSku;
  }

  // Listen for input changes to dynamically update the combined SKU
  if (skuPrefixInput && skuNumberInput && hiddenSkuInput) {
    skuPrefixInput.addEventListener("input", combineSku);
    skuNumberInput.addEventListener("input", combineSku);
    combineSku(); // Initial combination in case of pre-filled values (e.g., validation errors)
  }

  // Ensure SKU is combined just before form submission
  if (itemForm) {
    itemForm.addEventListener("submit", function () {
      combineSku();
    });
  }

  // --- Image Upload Preview Logic (remains the same) ---
  const imageInput = document.getElementById("id_image");
  const preview = document.getElementById("imagePreview");
  const previewWrapper = document.getElementById("imagePreviewWrapper");
  const placeholder = document.getElementById("imagePlaceholder");
  // Add hidden input for clearing image, as it's not in your provided HTML
  const clearImageHiddenInput = document.createElement("input");
  clearImageHiddenInput.type = "hidden";
  clearImageHiddenInput.name = "clear_image";
  clearImageHiddenInput.id = "id_clear_image";
  clearImageHiddenInput.value = "false";
  itemForm.appendChild(clearImageHiddenInput);

  /**
   * Reads the selected image file and displays it as a preview.
   * @param {HTMLInputElement} input The file input element.
   */
  function readURL(input) {
    if (input.files && input.files[0]) {
      const reader = new FileReader();
      reader.onload = function (e) {
        preview.src = e.target.result;
        preview.classList.remove("d-none");
        previewWrapper.classList.remove("d-none");
        placeholder.classList.add("d-none");
        clearImageHiddenInput.value = "false"; // New image selected, don't clear on save
      };
      reader.readAsDataURL(input.files[0]);
    } else {
      // No file selected (e.g., clear button pressed)
      preview.src = "#";
      preview.classList.add("d-none");
      previewWrapper.classList.add("d-none");
      placeholder.classList.remove("d-none");
      clearImageHiddenInput.value = "true"; // Signal to delete on server
    }
  }

  // Attach event listener for image input changes
  if (imageInput) {
    imageInput.addEventListener("change", function () {
      readURL(this);
    });
  }

  // Ensure the clear image button is available and works
  const clearImageBtn = document.getElementById("clearImageBtn");
  if (clearImageBtn) {
    clearImageBtn.addEventListener("click", function (e) {
      e.stopPropagation(); // Prevent click from bubbling to imageUploadContainer
      imageInput.value = ""; // Clear the file input
      readURL(null); // Reset the preview
    });
  }
});

// Global clearImage function for backward compatibility if onclick is used in HTML
window.clearImage = function (e) {
  e.stopPropagation(); // Prevent the click from re-opening the file dialog
  const imageInput = document.getElementById("id_image");
  const preview = document.getElementById("imagePreview");
  const previewWrapper = document.getElementById("imagePreviewWrapper");
  const placeholder = document.getElementById("imagePlaceholder");
  const clearImageHiddenInput = document.getElementById("id_clear_image");

  if (imageInput) {
    imageInput.value = ""; // Clear the file input value
  }
  if (previewWrapper) {
    previewWrapper.classList.add("d-none");
  }
  if (preview) {
    preview.src = "#"; // Reset image source to empty
  }
  if (placeholder) {
    placeholder.classList.remove("d-none");
  }
  if (clearImageHiddenInput) {
    clearImageHiddenInput.value = "true"; // Signal to delete on server
  }
};
