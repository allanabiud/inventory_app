document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("adjustmentForm");

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
    $(".select2-item").select2({
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
    const adjustmentTypeSelect = document.getElementById("id_adjustment_type");
    const quantityInput = document.getElementById("id_quantity_adjusted");
    const costPriceInput = document.getElementById("id_cost_price");
    const reasonSelect = document.getElementById("id_reason");

    let isValid = true;

    itemSelect.classList.remove("is-invalid");
    adjustmentTypeSelect.classList.remove("is-invalid");
    quantityInput.classList.remove("is-invalid");
    if (costPriceInput) costPriceInput.classList.remove("is-invalid");
    reasonSelect.classList.remove("is-invalid");

    if (!itemSelect.value) {
      displayMessage("Please select an item.");
      itemSelect.classList.add("is-invalid");
      isValid = false;
    }

    if (!adjustmentTypeSelect.value) {
      displayMessage("Please select an adjustment type.");
      adjustmentTypeSelect.classList.add("is-invalid");
      isValid = false;
    }

    const qty = parseInt(quantityInput.value);
    if (isNaN(qty) || qty <= 0) {
      displayMessage("Quantity adjusted must be a number greater than 0.");
      quantityInput.classList.add("is-invalid");
      isValid = false;
    }

    if (costPriceInput && costPriceInput.value !== "") {
      const cost = parseFloat(costPriceInput.value);
      if (isNaN(cost) || cost < 0) {
        displayMessage("Cost price must be a non-negative number.");
        costPriceInput.classList.add("is-invalid");
        isValid = false;
      }
    }

    if (!reasonSelect.value) {
      displayMessage("Please select a reason for the adjustment.");
      reasonSelect.classList.add("is-invalid");
      isValid = false;
    }

    if (!isValid) {
      e.preventDefault();
    }
  });

  const adjustmentTypeSelect = document.getElementById("id_adjustment_type");
  const reasonSelect = document.getElementById("id_reason");
  const allReasonOptions = Array.from(reasonSelect.options);

  function assignReasonDataTypes() {
    allReasonOptions.forEach((option) => {
      if (!option.dataset.type) {
        const val = option.value;
        let dataType = "BOTH";
        if (
          val === "PURCHASE" ||
          val === "STOCK_COUNT_INCREASE" ||
          val === "OTHER_INCREASE"
        ) {
          dataType = "INCREASE";
        } else if (
          val === "SALE" ||
          val === "STOLEN" ||
          val === "DAMAGED" ||
          val === "STOCK_COUNT_DECREASE" ||
          val === "OTHER_DECREASE"
        ) {
          dataType = "DECREASE";
        }
        option.dataset.type = dataType;
      }
    });
  }

  function filterReasonOptions() {
    assignReasonDataTypes();

    const selectedAdjustmentType = adjustmentTypeSelect.value;
    const currentSelectedReason = reasonSelect.value;

    reasonSelect.innerHTML = "";

    let reasonFoundInFiltered = false;

    if (selectedAdjustmentType) {
      allReasonOptions.forEach((option) => {
        const dataType = option.dataset.type;
        if (
          option.value === "" ||
          dataType === selectedAdjustmentType ||
          dataType === "BOTH"
        ) {
          reasonSelect.appendChild(option.cloneNode(true));
          if (option.value === currentSelectedReason) {
            reasonFoundInFiltered = true;
          }
        }
      });
    } else {
      allReasonOptions.forEach((option) => {
        if (option.value === "") {
          reasonSelect.appendChild(option.cloneNode(true));
        }
      });
    }

    if (
      !selectedAdjustmentType ||
      (!reasonFoundInFiltered && currentSelectedReason !== "")
    ) {
      reasonSelect.value = "";
    } else {
      reasonSelect.value = currentSelectedReason;
    }
  }

  adjustmentTypeSelect.addEventListener("change", filterReasonOptions);

  setTimeout(() => {
    filterReasonOptions();
  }, 10);
});
