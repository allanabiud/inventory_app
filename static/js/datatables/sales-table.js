document.addEventListener("DOMContentLoaded", function () {
  const table = $("#salesTable").DataTable({
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
        targets: 7,
        visible: true,
      },
    ],
    order: [[7, "desc"]],
  });

  // Move export buttons to a custom container
  table.buttons().container().appendTo("#exportButtonsContainer");

  // Style search box and dropdown
  $(".dataTables_length select").addClass("form-select form-select-sm");
  $(".dataTables_filter input")
    .addClass("form-control form-control-sm")
    .attr("placeholder", "Search sales...");

  // Remove default "Search:" label text
  $(".dataTables_filter label")
    .contents()
    .filter(function () {
      return this.nodeType === 3;
    })
    .remove();

  // Adjust columns and recalculate responsiveness
  table.columns.adjust().responsive.recalc();
});
