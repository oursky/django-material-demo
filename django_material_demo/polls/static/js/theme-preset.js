$(document).ready(function() {
  $("[data-theme-preset]").on("click", function() {
    $(`input[name="primary_color"]`).val($(this).data("theme-preset-primary-color"));
    $(`input[name="primary_color_light"]`).val($(this).data("theme-preset-primary-color-light"));
    $(`input[name="primary_color_dark"]`).val($(this).data("theme-preset-primary-color-dark"));
    $(`input[name="secondary_color"]`).val($(this).data("theme-preset-secondary-color"));
    $(`input[name="secondary_color_light"]`).val($(this).data("theme-preset-secondary-color-light"));
    $(`input[name="success_color"]`).val($(this).data("theme-preset-success-color"));
    $(`input[name="error_color"]`).val($(this).data("theme-preset-error-color"));
    $(`input[name="link_color"]`).val($(this).data("theme-preset-link-color"));
  });
});
