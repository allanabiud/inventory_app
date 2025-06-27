(() => {
  const getStoredTheme = () => localStorage.getItem("theme");
  const setStoredTheme = (theme) => localStorage.setItem("theme", theme);

  // We no longer need getPreferredTheme here as it's handled by the inline script
  // for initial load. We only need it on toggle to decide the next theme.

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
        "text-white", // Keep this if you want the icon to always be white
      );
    }
  };

  // Get the initial theme that was set by the inline script (or default by CSS)
  // This ensures the icon updates correctly on initial load
  const initialTheme =
    document.documentElement.getAttribute("data-bs-theme") ||
    getPreferredTheme(); // Fallback in case inline script wasn't perfect
  updateIcon(initialTheme);

  // Now, attach the event listener directly for the toggle button
  // No need for DOMContentLoaded since this script is deferred.
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
