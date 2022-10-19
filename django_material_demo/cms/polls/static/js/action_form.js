"use strict";
{
  $("#action-form").on("submit", function (event) {
    var form = this;
    var dataTable = $("dmc-datatable")[0]._datatable;
    var rowsSelected = dataTable.column(0).checkboxes.selected();

    if (!rowsSelected.length || $(form).find('*[name="action"]').val() == "") {
      event.preventDefault();
      return;
    }

    form.querySelectorAll("button").forEach(button => (button.disabled = true));

    $(form).append(
      $("<input>")
        .attr("type", "hidden")
        .attr("name", "submit_type")
        .val("action")
    );

    $.each(rowsSelected, function (index, rowId) {
      $(form).append(
        $("<input>").attr("type", "hidden").attr("name", "pk[]").val(rowId)
      );
    });
  });
}
