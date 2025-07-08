odoo.define("writer.column_toggle", function (require) {
  "use strict";
  var publicWidget = require("web.public.widget");

  publicWidget.registry.ColumnToggle = publicWidget.Widget.extend({
    selector: ".o_portal_table, .table",
    start: function () {
      // Listen for changes on all toggles
      document.querySelectorAll(".o_column_toggle").forEach(function (toggle) {
        toggle.addEventListener("change", function () {
          var col = parseInt(this.getAttribute("data-col"));
          var checked = this.checked;
          // Find all tables in the view
          document.querySelectorAll("table").forEach(function (table) {
            // Hide/show th
            table.querySelectorAll("thead th:nth-child(" + col + ")").forEach(function (th) {
              th.style.display = checked ? "" : "none";
            });
            // Hide/show td
            table
              .querySelectorAll("tbody td:nth-child(" + col + "), tbody th:nth-child(" + col + ")")
              .forEach(function (cell) {
                cell.style.display = checked ? "" : "none";
              });
          });
        });
      });
    },
  });

  return publicWidget.registry.ColumnToggle;
});
