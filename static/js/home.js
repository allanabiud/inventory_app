document.addEventListener("DOMContentLoaded", function () {
  // Initialize Bootstrap toasts
  document.querySelectorAll(".toast").forEach(function (toastEl) {
    const toast = new bootstrap.Toast(toastEl);
    toast.show();
  });

  // Initialize Bootstrap tooltips
  document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach((el) => {
    new bootstrap.Tooltip(el);
  });
});
