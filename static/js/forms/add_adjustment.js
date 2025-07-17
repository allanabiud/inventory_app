document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("adjustmentForm");

  // Initialize Select2
  // Ensure jQuery and Select2 libraries are loaded before this script runs
  if ($.fn.select2) {
    $(".select2-item").select2({
      theme: "bootstrap-5",
      placeholder: "Select an item",
      width: "100%", // Ensure it matches the parent width
      allowClear: true,
    });
  }

  // Client-side validation for form submission
  form.addEventListener("submit", function (e) {
    const qty = document.getElementById("id_quantity_adjusted").value;
    const item = document.getElementById("id_item").value;

    if (!item) {
      alert("Please select an item.");
      e.preventDefault();
      return; // Stop further validation
    }

    if (!qty || parseInt(qty) <= 0) {
      alert("Quantity adjusted must be greater than 0.");
      e.preventDefault();
      return; // Stop further validation
    }

    const reasonSelect = document.getElementById("id_reason");
    if (!reasonSelect.value) {
      alert("Please select a reason for the adjustment.");
      e.preventDefault();
      return;
    }
  });

  // Dynamic filtering of reasons based on adjustment type
  const adjustmentTypeRadios = document.querySelectorAll(
    'input[name="adjustment_type"]',
  );
  const reasonSelect = document.getElementById("id_reason");
  // Get all options initially, including the placeholder/empty option
  const reasonOptions = Array.from(reasonSelect.querySelectorAll("option"));

  function filterReasonOptions() {
    const selectedAdjustmentType = document.querySelector(
      'input[name="adjustment_type"]:checked',
    );
    const currentSelectedReason = reasonSelect.value; // Store the currently selected reason

    // Hide all options initially, except the placeholder
    reasonOptions.forEach((option) => {
      if (option.value === "") {
        // Keep the placeholder/empty option visible
        option.style.display = "";
      } else {
        option.style.display = "none";
      }
    });

    if (selectedAdjustmentType) {
      const type = selectedAdjustmentType.value; // "INCREASE" or "DECREASE"

      let reasonFoundInFiltered = false; // Flag to check if previously selected reason is still valid

      reasonOptions.forEach((option) => {
        const dataType = option.dataset.type; // Get the data-type attribute from the option

        // Show options that match the selected type, or are type "BOTH", or are the empty placeholder
        if (option.value === "" || dataType === type || dataType === "BOTH") {
          option.style.display = ""; // Make the option visible
          if (option.value === currentSelectedReason) {
            reasonFoundInFiltered = true; // The previously selected reason is valid for this type
          }
        }
      });

      // If the previously selected reason is no longer valid, or if no type was selected, reset
      if (!reasonFoundInFiltered && currentSelectedReason !== "") {
        reasonSelect.value = ""; // Reset the selection
      }
    } else {
      // If no adjustment type is selected, make sure no specific reason is selected either
      reasonSelect.value = "";
    }
  }

  // Add event listeners to the adjustment type radio buttons
  adjustmentTypeRadios.forEach((radio) => {
    radio.addEventListener("change", filterReasonOptions);
  });

  // Call the function on page load to set the initial state
  filterReasonOptions();
});
