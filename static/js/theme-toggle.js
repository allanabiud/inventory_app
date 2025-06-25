(() => {
  const getStoredTheme = () => localStorage.getItem("theme");

  const setStoredTheme = (theme) => localStorage.setItem("theme", theme);

  const getPreferredTheme = () => {
    const stored = getStoredTheme();
    if (stored) return stored;

    return window.matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light";
  };

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
        "text-white",
      );
    }
  };

  document.addEventListener("DOMContentLoaded", () => {
    const toggle = document.getElementById("theme-toggle");
    const preferred = getPreferredTheme();

    // Apply the initial theme based on preference or storage
    setTheme(preferred);

    if (toggle) {
      toggle.addEventListener("click", () => {
        const current = document.documentElement.getAttribute("data-bs-theme");
        const next = current === "dark" ? "light" : "dark";
        setStoredTheme(next);
        setTheme(next);
      });
    }
  });
})();
