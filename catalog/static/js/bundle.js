(() => {
  // frontend/app.ts
  var intSelect = (ctx, selector) => {
    const select = document.querySelector(selector);
    if (!select) {
      return ctx.console.error("Select doesn't exist");
    }
    select.addEventListener("input", (e) => {
      if (!(e.target instanceof HTMLInputElement)) {
        return;
      }
      ctx.console.log(e.target.value);
    });
  };

  // frontend/index.ts
  window.addEventListener("load", () => {
    intSelect(window, ".search-select");
  });
})();
