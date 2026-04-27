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

  const mobileMenuButton = document.querySelector(".mobile-menu-button");
  const mobileNav = document.getElementById("mobileNav");

  if (mobileMenuButton && mobileNav) {
    mobileMenuButton.addEventListener("click", () => {
      const isOpen = mobileMenuButton.getAttribute("aria-expanded") === "true";
      mobileMenuButton.setAttribute("aria-expanded", String(!isOpen));
      mobileNav.hidden = isOpen;
    });

    mobileNav.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => {
        mobileMenuButton.setAttribute("aria-expanded", "false");
        mobileNav.hidden = true;
      });
    });
  }
})();
