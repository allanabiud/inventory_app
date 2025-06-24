document.addEventListener("DOMContentLoaded", () => {
  const sidebar = document.getElementById("sidebar");
  const toggleBtn = document.getElementById("sidebarToggle");
  const toggleIcon = document.getElementById("sidebarToggleIcon");
  const sidebarItems = document.querySelectorAll(".sidebar-item"); // Select all main sidebar items

  const COLLAPSED_KEY = "sidebar-collapsed";

  // Function to apply the sidebar's visual state (collapsed or expanded)
  function applyState(collapsed) {
    if (collapsed) {
      sidebar.classList.add("collapsed");
      sidebar.style.width = "74px"; // Your preferred collapsed width
      toggleIcon.classList.replace("bi-chevron-left", "bi-chevron-right");

      // Close any currently open Bootstrap dropdowns when collapsing
      document
        .querySelectorAll("#sidebar .collapse.show")
        .forEach((collapseElement) => {
          const bsCollapse = bootstrap.Collapse.getInstance(collapseElement);
          if (bsCollapse) {
            bsCollapse.hide();
          }
        });
    } else {
      sidebar.classList.remove("collapsed");
      sidebar.style.width = "220px"; // Your preferred expanded width
      toggleIcon.classList.replace("bi-chevron-right", "bi-chevron-left");
    }
  }

  // --- Initialization ---
  const savedState = localStorage.getItem(COLLAPSED_KEY);
  applyState(savedState === "true"); // Apply saved state on page load

  // --- Event Listener for Main Toggle Button ---
  toggleBtn.addEventListener("click", () => {
    const isNowCollapsed = !sidebar.classList.contains("collapsed");
    localStorage.setItem(COLLAPSED_KEY, isNowCollapsed);
    applyState(isNowCollapsed);
  });

  // --- Event Listeners for Sidebar Items (Click to Expand) ---
  sidebarItems.forEach((item) => {
    item.addEventListener("click", function (event) {
      // Check if the sidebar is currently collapsed
      if (sidebar.classList.contains("collapsed")) {
        event.preventDefault(); // Prevent default link/dropdown behavior immediately

        // Expand the sidebar
        const isNowCollapsed = false; // We want to expand it
        localStorage.setItem(COLLAPSED_KEY, isNowCollapsed);
        applyState(isNowCollapsed);

        // Get the transition duration from CSS for a smooth follow-up action
        const transitionDuration =
          parseFloat(getComputedStyle(sidebar).transitionDuration) * 1000;

        // After a short delay (allowing sidebar to expand), trigger the item's original action
        setTimeout(() => {
          if (this.dataset.bsToggle === "collapse") {
            // If it's a dropdown, explicitly toggle its collapse state
            const targetId = this.getAttribute("href");
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
              // --- START OF MODIFICATION ---
              // Only call toggle if the element is not already open.
              // This prevents the "expand then close" behavior.
              if (!targetElement.classList.contains("show")) {
                new bootstrap.Collapse(targetElement, { toggle: true });
              }
              // --- END OF MODIFICATION ---
            }
          } else if (this.href && this.href !== "#") {
            // If it's a regular link, navigate to its URL
            window.location.href = this.href;
          }
        }, transitionDuration + 50); // Add a small buffer (50ms) for smoother transition
      }
      // If sidebar is already expanded, let the default click event occur
      // (Bootstrap handles dropdowns, and browser handles regular links)
    });
  });
});
