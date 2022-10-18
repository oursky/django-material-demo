"use strict";
(function () {
  function init() {
    M.Range.init($("input[type=range]"));
  }
  if (document.readyState === "complete") {
    init();
  } else {
    document.addEventListener("turbolinks:load", init, { once: true });
  }
  document.addEventListener("turbolinks:render", init);
})();
