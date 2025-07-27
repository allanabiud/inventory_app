document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("salesForm");

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
    $(".select2-item, .select2-customer").select2({
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
    const quantityInput = document.getElementById("id_quantity_sold");
    const priceInput = document.getElementById("id_unit_price");
    const descriptionInput = document.getElementById("id_description");

    let isValid = true;

    itemSelect.classList.remove("is-invalid");
    quantityInput.classList.remove("is-invalid");
    priceInput.classList.remove("is-invalid");

    if (!itemSelect.value) {
      displayMessage("Please select an item.");
      itemSelect.classList.add("is-invalid");
      isValid = false;
    }

    const qty = parseInt(quantityInput.value);
    if (isNaN(qty) || qty <= 0) {
      displayMessage("Quantity sold must be a number greater than 0.");
      quantityInput.classList.add("is-invalid");
      isValid = false;
    }

    const price = parseFloat(priceInput.value);
    if (isNaN(price) || price < 0) {
      displayMessage("Unit price must be a non-negative number.");
      priceInput.classList.add("is-invalid");
      isValid = false;
    }

    if (!isValid) {
      e.preventDefault();
    }
  });
});
