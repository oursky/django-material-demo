"use strict";
{
  function reloadForm(e) {
    // exclude csrfmiddlewaretoken since it is regenerated when form reloads
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
    // allow only one execution since handler is reattached on each form reload
    $(document).one("change", "input[data-reload-form]", reloadForm);
  });
}
