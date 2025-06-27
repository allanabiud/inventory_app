document.addEventListener("DOMContentLoaded", () => {
  const sidebar = document.getElementById("sidebar");
  const toggleBtn = document.getElementById("sidebarToggle");
  const toggleIcon = document.getElementById("sidebarToggleIcon");
  const sidebarItems = document.querySelectorAll(".sidebar-item");

  const COLLAPSED_KEY = "sidebar-collapsed";
  const OPEN_COLLAPSE_KEY = "sidebar-open-collapse";

  const popoverInstances = new Map();
  let currentPopoverOwner = null;

  function hidePopover() {
    if (currentPopoverOwner) {
      popoverInstances.get(currentPopoverOwner)?.hide();
      currentPopoverOwner = null;
    }
  }

  function setupPopovers(enable) {
    sidebarItems.forEach((item) => {
      const targetId = item.getAttribute("href");
      const isCollapse = targetId?.startsWith("#");
      const collapseEl = isCollapse && document.querySelector(targetId);

      if (isCollapse && collapseEl) {
        item.setAttribute("aria-haspopup", "true");

        if (enable && !popoverInstances.has(item)) {
          const popover = new bootstrap.Popover(item, {
            html: true,
            placement: "right",
            trigger: "manual",
            container: "body",
            content: collapseEl.innerHTML,
            customClass: "sidebar-popover-custom",
          });

          popoverInstances.set(item, popover);
        } else if (!enable && popoverInstances.has(item)) {
          popoverInstances.get(item).dispose();
          popoverInstances.delete(item);
        }
      }
    });
  }

  function applySidebarState(collapsed) {
    sidebar.classList.toggle("collapsed", collapsed);
    toggleIcon.classList.replace(
      collapsed ? "bi-chevron-left" : "bi-chevron-right",
      collapsed ? "bi-chevron-right" : "bi-chevron-left",
    );

    const mainContent = document.getElementById("main-content");
    if (mainContent) {
      mainContent.style.marginLeft = collapsed ? "74px" : "200px";
    }

    sidebarItems.forEach((item) => {
      const isCollapse = item.dataset.bsToggle === "collapse";

      if (collapsed) {
        if (isCollapse) {
          // Store original data-bs-toggle for restoration
          if (!item.dataset.originalBsToggle) {
            // Only store if not already stored
            item.dataset.originalBsToggle = "collapse";
          }
          item.removeAttribute("data-bs-toggle"); // Remove to prevent collapse from triggering directly
        }
      } else {
        // Sidebar is expanded
        if (item.dataset.originalBsToggle === "collapse") {
          item.setAttribute("data-bs-toggle", "collapse"); // Restore data-bs-toggle
          delete item.dataset.originalBsToggle; // Clean up
        }
      }
    });

    if (collapsed) {
      // When collapsing, hide any currently open sub-menus
      document.querySelectorAll("#sidebar .collapse.show").forEach((el) => {
        const bsCollapse = bootstrap.Collapse.getInstance(el);
        if (bsCollapse) {
          bsCollapse.hide();
          // Do NOT remove from localStorage here, as it might be needed for re-expansion
        }
      });
      setupPopovers(true); // Enable popovers for collapsed state
    } else {
      // Sidebar is expanded
      hidePopover(); // Hide any active popover
      setupPopovers(false); // Disable popovers

      // Re-open the last active collapse, or the one belonging to the active sub-item
      const lastOpenId = localStorage.getItem(OPEN_COLLAPSE_KEY);
      const activeSubItem = document.querySelector(".sidebar-sub-item.active");
      let toOpenEl = null;

      if (activeSubItem) {
        // If an active sub-item exists, find its parent collapse
        toOpenEl = activeSubItem.closest(".collapse");
      } else if (lastOpenId) {
        // Otherwise, try to open the one that was last open
        toOpenEl = document.querySelector(lastOpenId);
      }

      if (toOpenEl && !toOpenEl.classList.contains("show")) {
        // Ensure it's not already shown to avoid redundant toggles
        new bootstrap.Collapse(toOpenEl, { toggle: true });
        // Set aria-expanded on the parent sidebar-item
        const parentSidebarItem = document.querySelector(
          `[href="#${toOpenEl.id}"]`,
        );
        if (parentSidebarItem) {
          parentSidebarItem.setAttribute("aria-expanded", "true");
        }
      }
    }
  }

  // --- Initial Load Logic ---
  const storedCollapsedState = localStorage.getItem(COLLAPSED_KEY);
  // Default to false (expanded) if no state is stored, or if stored as "false"
  // Default to true (collapsed) if stored as "true"
  const isCollapsed = storedCollapsedState === "true";

  applySidebarState(isCollapsed); // Apply the stored/default state immediately

  // --- Event Listeners ---
  toggleBtn.addEventListener("click", () => {
    const newState = !sidebar.classList.contains("collapsed"); // Get the *new* state after toggle
    localStorage.setItem(COLLAPSED_KEY, newState.toString()); // Store as "true" or "false"
    applySidebarState(newState); // Apply the new state
  });

  // Sidebar item click handler (main navigation and collapse toggles)
  sidebar.addEventListener("click", (e) => {
    const item = e.target.closest(".sidebar-item");
    if (!item) return;

    const href = item.getAttribute("href");
    const isCollapseTrigger =
      item.dataset.bsToggle === "collapse" ||
      item.dataset.originalBsToggle === "collapse"; // Check both

    if (sidebar.classList.contains("collapsed")) {
      e.preventDefault(); // Prevent default if sidebar is collapsed (for popovers/navigation)

      if (isCollapseTrigger) {
        // This item triggers a collapse (now a popover)
        if (popoverInstances.has(item)) {
          const popover = popoverInstances.get(item);

          if (currentPopoverOwner === item) {
            hidePopover(); // Hide if clicking the same item
          } else {
            hidePopover(); // Hide any other open popover
            popover.show(); // Show current item's popover
            currentPopoverOwner = item;
          }
        }
      } else if (href && href !== "#") {
        // Regular navigation link when collapsed
        window.location.href = href;
      }
    } else {
      // Sidebar is expanded
      if (isCollapseTrigger && href) {
        // This is a collapse toggle in expanded mode
        e.preventDefault(); // prevent default anchor scroll
        const target = document.querySelector(href);
        if (!target) return;

        const isOpen = target.classList.contains("show");

        if (!isOpen) {
          // If about to open, close others
          document.querySelectorAll("#sidebar .collapse.show").forEach((el) => {
            if (el !== target) {
              bootstrap.Collapse.getInstance(el)?.hide();
            }
          });
          // Show current collapse
          const instance =
            bootstrap.Collapse.getInstance(target) ||
            new bootstrap.Collapse(target, { toggle: false });
          instance.show();
          localStorage.setItem(OPEN_COLLAPSE_KEY, href); // Store which one is open
        } else {
          // If about to close
          bootstrap.Collapse.getInstance(target)?.hide();
          localStorage.removeItem(OPEN_COLLAPSE_KEY); // Remove from storage when closed
        }
      } else if (href && href !== "#") {
        // Regular navigation link when expanded
        window.location.href = href;
        // If navigating away, it might be good to clear the last open collapse,
        // unless you want it to persist when returning to the same parent route.
        // localStorage.removeItem(OPEN_COLLAPSE_KEY);
      }
    }
  });

  // Popover sub-item click
  document.body.addEventListener("click", (e) => {
    const subItem = e.target.closest(".sidebar-sub-item");
    const inPopover = e.target.closest(".popover.show");

    if (subItem?.href && subItem.href !== "#" && inPopover) {
      e.preventDefault();
      window.location.href = subItem.href;
      hidePopover();

      // Store the parent collapse of the clicked sub-item so it re-opens if sidebar expands
      const parentCollapse = subItem.closest(".collapse");
      if (parentCollapse) {
        localStorage.setItem(OPEN_COLLAPSE_KEY, `#${parentCollapse.id}`);
      }
    }
  });

  // Close popover when clicking outside
  document.addEventListener("click", (e) => {
    const insidePopover = e.target.closest(".popover");
    const insideTrigger = e.target.closest(".sidebar-item"); // Exclude the trigger itself

    if (!insidePopover && !insideTrigger) {
      hidePopover();
    }
  });

  // Listener for Bootstrap Collapse events
  // This is important to keep OPEN_COLLAPPSE_KEY in sync if collapses are toggled by other means
  // or if they finish their animation.
  document.querySelectorAll("#sidebar .collapse").forEach((collapseEl) => {
    collapseEl.addEventListener("hidden.bs.collapse", function () {
      if (localStorage.getItem(OPEN_COLLAPSE_KEY) === `#${this.id}`) {
        localStorage.removeItem(OPEN_COLLAPSE_KEY);
      }
      // Update aria-expanded on parent
      const parentSidebarItem = document.querySelector(`[href="#${this.id}"]`);
      if (parentSidebarItem) {
        parentSidebarItem.setAttribute("aria-expanded", "false");
      }
    });

    collapseEl.addEventListener("shown.bs.collapse", function () {
      localStorage.setItem(OPEN_COLLAPSE_KEY, `#${this.id}`);
      // Update aria-expanded on parent
      const parentSidebarItem = document.querySelector(`[href="#${this.id}"]`);
      if (parentSidebarItem) {
        parentSidebarItem.setAttribute("aria-expanded", "true");
      }
    });
  });
});
