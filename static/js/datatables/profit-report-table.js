document.addEventListener("DOMContentLoaded", function () {
  const table = $("#profitReportTable").DataTable({
    paging: true,
    pageLength: 10,
    lengthChange: true,
    searching: true,
    ordering: true,
    info: true,
    responsive: true,
    autoWidth: false,
    dom: "lBfrtip",
    order: [[5, "desc"]],
    buttons: [
      {
        extend: "collection",
        className: "btn btn-outline-secondary dropdown-toggle",
        text: '<i class="bi bi-download me-1"></i> Export',
        buttons: [
          {
            extend: "excelHtml5",
            title: "Profit Report",
            className: "dropdown-item",
          },
          {
            extend: "csvHtml5",
            title: "Profit Report",
            className: "dropdown-item",
          },
          {
            extend: "pdfHtml5",
            title: "Profit Report",
            orientation: "landscape",
            pageSize: "A4",
            className: "dropdown-item",
          },
          {
            extend: "print",
            title: "Profit Report",
            className: "dropdown-item",
          },
        ],
      },
    ],
  });

  // move built-in controls to custom containers
  table.buttons().container().appendTo("#exportButtonsContainer");
  $(".dataTables_filter").appendTo("#searchContainer");
  $(".dataTables_length").appendTo("#lengthContainer");

  // style customization
  $(".dataTables_length select").addClass("form-select form-select-sm");
  $(".dataTables_filter input")
    .addClass("form-control form-control-sm")
    .attr("placeholder", "Search profits...");

  // remove the default label text from the search box
  $(".dataTables_filter label")
    .contents()
    .filter(function () {
      return this.nodeType === 3;
    })
    .remove();

  table.columns.adjust().responsive.recalc();

  table.draw();
});
