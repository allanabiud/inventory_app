document.addEventListener("DOMContentLoaded", function () {
  const table = $("#adjustmentsTable").DataTable({
    paging: true,
    pageLength: 10,
    lengthChange: true,
    searching: true,
    ordering: true,
    order: [[0, "desc"]], // Default order by date (column index 0)
    info: true,
    responsive: true,
    autoWidth: false,
    dom:
      "<'row align-items-center mb-3'<'col-md-6 d-flex justify-content-start'f><'col-md-6 d-flex justify-content-end'l>>" +
      "<'row'<'col-12'tr>>" +
      "<'row mt-2'<'col-md-6'i><'col-md-6'p>>",
    columnDefs: [
      { targets: [1, 2, 3, 4, 5], orderable: false }, // Optional: disable sort on some columns
    ],
  });

  $(".dataTables_length select").addClass("form-select form-select-sm");
  $(".dataTables_filter input")
    .addClass("form-control form-control-sm")
    .attr("placeholder", "Search adjustments...");
  $(".dataTables_filter label")
    .contents()
    .filter(function () {
      return this.nodeType === 3;
    })
    .remove();

  table.columns.adjust().responsive.recalc();
});
