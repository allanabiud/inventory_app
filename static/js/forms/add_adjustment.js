document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("adjustmentForm");

  $(".select2-item").select2({
    theme: "bootstrap-5",
    placeholder: "Select an item",
    width: "100%", // Ensure it matches the parent width
    allowClear: true,
  });

  form.addEventListener("submit", function (e) {
    const qty = document.getElementById("id_quantity_adjusted").value;
    const item = document.getElementById("id_item").value;

    if (!item) {
      alert("Please select an item.");
      e.preventDefault();
    }

    if (!qty || parseInt(qty) <= 0) {
      alert("Quantity adjusted must be greater than 0.");
      e.preventDefault();
    }
  });
});
