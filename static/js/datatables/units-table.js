document.addEventListener("DOMContentLoaded", function () {
  const table = $("#unitsTable").DataTable({
    paging: true,
    pageLength: 10,
    lengthChange: true,
    searching: true,
    ordering: true,
    info: true,
    responsive: true,
    autoWidth: false,
    dom:
      "<'row align-items-center mb-3'<'col-md-6 d-flex justify-content-start'f><'col-md-6 d-flex justify-content-end'l>>" +
      "<'row'<'col-12'tr>>" +
      "<'row mt-2'<'col-md-6'i><'col-md-6'p>>",
    columnDefs: [
      { targets: 2, orderable: false }, // Make 'Description' unsortable
    ],
  });

  $(".dataTables_length select").addClass("form-select form-select-sm");
  $(".dataTables_filter input")
    .addClass("form-control form-control-sm")
    .attr("placeholder", "Search units...");
  $(".dataTables_filter label")
    .contents()
    .filter(function () {
      return this.nodeType === 3;
    })
    .remove();

  table.columns.adjust().responsive.recalc();
});
