document.addEventListener("DOMContentLoaded", function () {
  // --- Inventory Tracking Logic ---
  const trackInventoryCheckbox = document.getElementById("id_track_inventory");
  const inventoryFieldsContainer = document.getElementById(
    "inventoryFieldsContainer",
  );

  // Get references to the inventory input fields
  const openingStockInput = document.getElementById("id_opening_stock");
  const currentStockInput = document.getElementById("id_current_stock");
  const reorderPointInput = document.getElementById("id_reorder_point");

  /**
   * Toggles the visibility and 'required' attribute of inventory-related fields
   * based on the state of the 'track inventory' checkbox.
   */
  function toggleInventoryFields() {
    const isChecked = trackInventoryCheckbox.checked;
    if (isChecked) {
      inventoryFieldsContainer.classList.remove("d-none");
      // Mark fields as required for client-side hint, server handles actual validation
      openingStockInput.setAttribute("required", "true");
      // current_stock can be derived on the server if not provided, so not strictly required client-side
      currentStockInput.removeAttribute("required");
      reorderPointInput.setAttribute("required", "true");
    } else {
      inventoryFieldsContainer.classList.add("d-none");
      // Remove required attribute and clear values when inventory is not tracked
      openingStockInput.removeAttribute("required");
      currentStockInput.removeAttribute("required");
      reorderPointInput.removeAttribute("required");

      openingStockInput.value = "";
      currentStockInput.value = "";
      reorderPointInput.value = "";
    }
  }

  // Initialize and attach event listener for inventory tracking
  if (trackInventoryCheckbox && inventoryFieldsContainer) {
    toggleInventoryFields(); // Set initial state on page load
    trackInventoryCheckbox.addEventListener("change", toggleInventoryFields);
  }

  // --- SKU Combination Logic ---
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

  // --- Image Upload Preview Logic ---
  const imageInput = document.getElementById("id_image");
  const preview = document.getElementById("imagePreview");
  const previewWrapper = document.getElementById("imagePreviewWrapper");
  const placeholder = document.getElementById("imagePlaceholder");

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
      };
      reader.readAsDataURL(input.files[0]);
    }
  }

  // Attach event listener for image input changes
  if (imageInput) {
    imageInput.addEventListener("change", function () {
      readURL(this);
    });
  }

  /**
   * Clears the selected image, resets the preview, and shows the placeholder.
   * This function is made global to be called directly from an `onclick` HTML attribute.
   * @param {Event} e The event object from the button click.
   */
  window.clearImage = function (e) {
    e.stopPropagation(); // Prevent the click from re-opening the file dialog
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
  };
});
