document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("purchaseForm");

  function displayMessage(message, type = "danger") {
    let container = form.querySelector(".messages-container");
    if (!container) {
      container = document.createElement("div");
      container.className = "messages-container mb-3";
      const csrfToken = form.querySelector('input[name="csrfmiddlewaretoken"]');
      csrfToken?.parentNode.insertBefore(container, csrfToken.nextSibling);
    }
    container.innerHTML = `
      <div class="alert alert-${type} alert-dismissible fade show" role="alert">
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
      </div>
    `;
  }

  if (typeof jQuery !== "undefined" && $.fn.select2) {
    $(".select2-item, .select2-supplier").select2({
      theme: "bootstrap-5",
      placeholder: $(this).data("placeholder") || "Select an option",
      width: "100%",
      allowClear: true,
    });
  }

  form.addEventListener("submit", function (e) {
    const itemSelect = document.getElementById("id_item");
    const qtyInput = document.getElementById("id_quantity_purchased");
    const priceInput = document.getElementById("id_unit_price");

    let isValid = true;
    itemSelect.classList.remove("is-invalid");
    qtyInput.classList.remove("is-invalid");
    priceInput.classList.remove("is-invalid");

    if (!itemSelect.value) {
      displayMessage("Please select an item.");
      itemSelect.classList.add("is-invalid");
      isValid = false;
    }

    const qty = parseInt(qtyInput.value);
    if (isNaN(qty) || qty <= 0) {
      displayMessage("Quantity must be a number greater than 0.");
      qtyInput.classList.add("is-invalid");
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
