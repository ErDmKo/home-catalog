declare global {
  interface Window {
    console: Console
  }
}
export const intSelect = (ctx: Window, selector: string) => {
  const select = document.querySelector(selector);
  if (!select) {
    return ctx.console.error("Select doesn't exist")
  }
  select.addEventListener('input', (e) => {
    if (!(e.target instanceof HTMLInputElement)) {
      return;
    }
    ctx.console.log(e.target.value);
  })
}
