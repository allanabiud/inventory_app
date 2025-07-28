document.addEventListener("DOMContentLoaded", function () {
  const table = $("#purchasesTable").DataTable({
    paging: true,
    pageLength: 10,
    lengthChange: true,
    searching: true,
    ordering: true,
    info: true,
    responsive: true,
    autoWidth: false,
    dom:
      "<'row align-items-center mb-3'<'col-md-6 d-flex justify-content-start' f><'col-md-6 d-flex justify-content-end' l>>" +
      "<'row'<'col-12'tr>>" +
      "<'row mt-2'<'col-md-6'i><'col-md-6'p>>",
    buttons: [
      {
        extend: "collection",
        className: "btn btn-secondary",
        text: '<i class="bi bi-download me-1"></i> Export',
        buttons: [
          { extend: "excel", className: "dropdown-item" },
          { extend: "csv", className: "dropdown-item" },
          { extend: "pdf", className: "dropdown-item" },
          { extend: "print", className: "dropdown-item" },
        ],
      },
    ],
    columnDefs: [
      {
        targets: 6,
        visible: true,
      },
    ],
    order: [[6, "desc"]],
  });

  table.buttons().container().appendTo("#exportPurchasesButtonsContainer");

  $(".dataTables_length select").addClass("form-select form-select-sm");
  $(".dataTables_filter input")
    .addClass("form-control form-control-sm")
    .attr("placeholder", "Search purchases...");

  $(".dataTables_filter label")
    .contents()
    .filter(function () {
      return this.nodeType === 3;
    })
    .remove();

  table.columns.adjust().responsive.recalc();
});
