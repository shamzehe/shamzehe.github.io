// Small enhancements: theme toggle, spam-resistant email links, mobile menu.
(() => {
  const root = document.documentElement;

  // Theme toggle — remembers the visitor's choice; otherwise follows the system.
  const toggle = document.querySelector(".theme-toggle");
  const systemDark = window.matchMedia("(prefers-color-scheme: dark)");
  const currentTheme = () => root.getAttribute("data-theme") || (systemDark.matches ? "dark" : "light");
  const syncToggle = () => toggle && toggle.setAttribute("aria-pressed", String(currentTheme() === "dark"));
  if (toggle) {
    toggle.addEventListener("click", () => {
      const next = currentTheme() === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", next);
      try { localStorage.setItem("theme", next); } catch (e) { /* private mode: still switches */ }
      syncToggle();
    });
    systemDark.addEventListener("change", syncToggle);
    syncToggle();
  }

  // Email links are assembled here so the address isn't in the page source.
  document.querySelectorAll("[data-email-user]").forEach((link) => {
    const address = `${link.dataset.emailUser}@${link.dataset.emailDomain}`;
    link.setAttribute("href", `mailto:${address}`);
    if (!link.getAttribute("title")) link.setAttribute("title", address);
    const text = link.querySelector("[data-email-text]");
    if (text) text.textContent = text.classList.contains("visually-hidden") ? `Email ${address}` : address;
  });

  // Mobile menu
  const navToggle = document.querySelector(".nav-toggle");
  const menu = document.getElementById("nav-menu");
  if (navToggle && menu) {
    const setOpen = (open) => {
      navToggle.setAttribute("aria-expanded", String(open));
      menu.classList.toggle("is-open", open);
    };
    navToggle.addEventListener("click", () => setOpen(navToggle.getAttribute("aria-expanded") !== "true"));
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && navToggle.getAttribute("aria-expanded") === "true") {
        setOpen(false);
        navToggle.focus();
      }
    });
    document.addEventListener("click", (event) => {
      if (!event.target.closest(".site-nav")) setOpen(false);
    });
  }
})();
