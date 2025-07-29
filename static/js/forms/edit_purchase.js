document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("purchaseForm"); // Changed form ID to match HTML

  function displayMessage(message, type = "danger") {
    let messageContainer = form.querySelector(".messages-container");
    if (!messageContainer) {
      messageContainer = document.createElement("div");
      messageContainer.className = "messages-container mb-3";
      const csrfToken = form.querySelector('input[name="csrfmiddlewaretoken"]');
      if (csrfToken) {
        csrfToken.parentNode.insertBefore(
          messageContainer,
          csrfToken.nextSibling,
        );
      } else {
        form.prepend(messageContainer);
      }
    }

    const alertDiv = document.createElement("div");
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.setAttribute("role", "alert");
    alertDiv.innerHTML = `
      ${message}
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    messageContainer.innerHTML = "";
    messageContainer.appendChild(alertDiv);
  }

  if (typeof jQuery !== "undefined" && $.fn.select2) {
    // Assuming you might use select2 for item and supplier fields
    $(".select2-item, .select2-supplier").select2({
      // Changed .select2-customer to .select2-supplier
      theme: "bootstrap-5",
      placeholder: $(this).data("placeholder") || "Select an option",
      width: "100%",
      allowClear: true,
    });
  }

  form.addEventListener("submit", function (e) {
    const messageContainer = form.querySelector(".messages-container");
    if (messageContainer) {
      messageContainer.innerHTML = "";
    }

    const itemSelect = document.getElementById("id_item");
    const quantityInput = document.getElementById("id_quantity"); // Changed to id_quantity
    const unitCostInput = document.getElementById("id_unit_cost"); // Changed to id_unit_cost
    const descriptionInput = document.getElementById("id_description"); // Remains the same

    let isValid = true;

    // Clear previous validation styles
    itemSelect.classList.remove("is-invalid");
    quantityInput.classList.remove("is-invalid");
    if (unitCostInput) {
      // unit_cost can be null/blank, so check if element exists
      unitCostInput.classList.remove("is-invalid");
    }

    if (!itemSelect.value) {
      displayMessage("Please select an item.");
      itemSelect.classList.add("is-invalid");
      isValid = false;
    }

    const qty = parseInt(quantityInput.value);
    if (isNaN(qty) || qty <= 0) {
      displayMessage("Quantity purchased must be a number greater than 0.");
      quantityInput.classList.add("is-invalid");
      isValid = false;
    }

    // Validation for unit_cost (can be null/blank on the model, but if provided, must be positive)
    if (unitCostInput && unitCostInput.value) {
      // Only validate if a value is entered
      const cost = parseFloat(unitCostInput.value);
      if (isNaN(cost) || cost <= 0) {
        // Changed price < 0 to cost <= 0 for unit_cost
        displayMessage("Unit cost must be a positive number.");
        unitCostInput.classList.add("is-invalid");
        isValid = false;
      }
    }

    if (!isValid) {
      e.preventDefault();
    }
  });
});
