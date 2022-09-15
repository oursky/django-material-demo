"use strict";
{
  function reloadForm(e) {
    let formSelector = "form :not(input[name=csrfmiddlewaretoken])";
    let formData = $(formSelector).serialize();
    let inputId = e.target.id;

    // add formData in GET request for initializing form with previous data
    Turbolinks.visit(
      window.location.origin +
        window.location.pathname +
        `?${formData}#${inputId}`,
      { action: "replace" }
    );
  }

  $(document).ready(function () {
    $(document).on("change", "input[data-reload-form]", reloadForm);
  });
}
