document.addEventListener("DOMContentLoaded", function () {
  const table = $("#itemsTable").DataTable({
    paging: true,
    pageLength: 10,
    lengthChange: true,
    searching: true,
    ordering: true,
    info: true,
    responsive: true,
    autoWidth: false,
    dom:
      // Wrap search and length in a full-width row
      "<'row align-items-center mb-3'<'col-md-6 d-flex justify-content-start' f><'col-md-6 d-flex justify-content-end' l>>" +
      // Table
      "<'row'<'col-12'tr>>" +
      // Bottom info and pagination
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
  });

  // Move export buttons to the custom container
  table.buttons().container().appendTo("#exportButtonsContainer");

  // Optional: Smaller controls
  $(".dataTables_length select").addClass("form-select form-select-sm");
  $(".dataTables_filter input").addClass("form-control form-control-sm");

  // Style inputs
  $(".dataTables_length select").addClass("form-select form-select-sm");
  $(".dataTables_filter input")
    .addClass("form-control form-control-sm")
    .attr("placeholder", "Search items..."); // <- Set placeholder

  // Remove "Search:" label
  $(".dataTables_filter label")
    .contents()
    .filter(function () {
      return this.nodeType === 3; // Node.TEXT_NODE
    })
    .remove();
});
