(function () {
  const firstAutofocus = document.querySelector("[data-autofocus]");
  if (firstAutofocus) {
    firstAutofocus.focus();
  }

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      const openDialog = document.querySelector("dialog[open]");
      if (openDialog) {
        openDialog.close();
      }
    }
  });
})();

