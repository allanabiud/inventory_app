(() => {
  const setStoredTheme = (theme) => localStorage.setItem("theme", theme);

  const setTheme = (theme) => {
    document.documentElement.setAttribute("data-bs-theme", theme);
    updateIcon(theme);
  };

  const updateIcon = (theme) => {
    const icon = document.getElementById("theme-icon");
    if (icon) {
      icon.className = "bi"; // reset
      icon.classList.add(
        theme === "dark" ? "bi-moon-stars-fill" : "bi-sun-fill",
      );
    }
  };

  // Get the initial theme that was set by the inline script (or default by CSS)
  const initialTheme =
    document.documentElement.getAttribute("data-bs-theme") ||
    getPreferredTheme(); // Fallback in case inline script wasn't perfect
  updateIcon(initialTheme);

  // attach the event listener directly for the toggle button
  const toggle = document.getElementById("theme-toggle");
  if (toggle) {
    toggle.addEventListener("click", () => {
      const current = document.documentElement.getAttribute("data-bs-theme");
      const next = current === "dark" ? "light" : "dark";
      setStoredTheme(next);
      setTheme(next);
    });
  }
})();
