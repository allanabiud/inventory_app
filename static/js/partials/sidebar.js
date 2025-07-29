document.addEventListener("DOMContentLoaded", () => {
  const sidebar = document.getElementById("sidebar");
  const toggleBtn = document.getElementById("sidebarToggle");
  const toggleIcon = document.getElementById("sidebarToggleIcon");
  const sidebarItems = document.querySelectorAll(".sidebar-item");

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

  function syncChevronRotation(item, isExpanded) {
    const chevron = item.querySelector(".sidebar-chevron");
    if (chevron) {
      if (isExpanded) {
        chevron.style.transform = "rotate(180deg)";
      } else {
        chevron.style.transform = "rotate(0deg)";
      }
    }
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
      const isCollapseTrigger =
        item.dataset.bsToggle === "collapse" ||
        item.dataset.originalBsToggle === "collapse";
      const href = item.getAttribute("href");
      const targetCollapse =
        href && href.startsWith("#") ? document.querySelector(href) : null;

      if (collapsed) {
        if (isCollapseTrigger) {
          if (!item.dataset.originalBsToggle) {
            item.dataset.originalBsToggle = "collapse";
          }
          item.removeAttribute("data-bs-toggle");
        }
        syncChevronRotation(item, false);
      } else {
        if (item.dataset.originalBsToggle === "collapse") {
          item.setAttribute("data-bs-toggle", "collapse");
          delete item.dataset.originalBsToggle;
        }

        if (targetCollapse) {
          syncChevronRotation(item, targetCollapse.classList.contains("show"));
        }
      }
    });

    if (collapsed) {
      document.querySelectorAll("#sidebar .collapse.show").forEach((el) => {
        const bsCollapse = bootstrap.Collapse.getInstance(el);
        if (bsCollapse) {
          bsCollapse.hide();
        }
      });
      setupPopovers(true);
    } else {
      hidePopover();
      setupPopovers(false);

      document.querySelectorAll("#sidebar .collapse").forEach((el) => {
        if (!el.classList.contains("show")) {
          const bsCollapse = bootstrap.Collapse.getInstance(el);
          if (
            bsCollapse &&
            (el.classList.contains("showing") || el.classList.contains("show"))
          ) {
            bsCollapse.hide();
          } else if (!bsCollapse && el.classList.contains("show")) {
            el.classList.remove("show");
            const parentSidebarItem = document.querySelector(
              `[href="#${el.id}"]`,
            );
            if (parentSidebarItem) {
              parentSidebarItem.setAttribute("aria-expanded", "false");
              syncChevronRotation(parentSidebarItem, false);
            }
          }
        }
      });
    }
  }

  // --- Initial Load Logic ---
  // Default to expanded state on every page load
  applySidebarState(false); // Set to true if you want it collapsed by default

  // Initial chevron sync for all items on page load
  sidebarItems.forEach((item) => {
    const href = item.getAttribute("href");
    if (href && href.startsWith("#")) {
      const targetCollapse = document.querySelector(href);
      if (targetCollapse) {
        syncChevronRotation(item, targetCollapse.classList.contains("show"));
      }
    }
  });

  // --- Event Listeners ---
  toggleBtn.addEventListener("click", () => {
    const newState = !sidebar.classList.contains("collapsed");
    applySidebarState(newState);
  });

  // Sidebar item click handler (main navigation and collapse toggles)
  sidebar.addEventListener("click", (e) => {
    const item = e.target.closest(".sidebar-item");
    if (!item) return;

    const href = item.getAttribute("href");
    const isCollapseTrigger =
      item.dataset.bsToggle === "collapse" ||
      item.dataset.originalBsToggle === "collapse";

    if (sidebar.classList.contains("collapsed")) {
      e.preventDefault();

      if (isCollapseTrigger) {
        if (popoverInstances.has(item)) {
          const popover = popoverInstances.get(item);
          if (currentPopoverOwner === item) {
            hidePopover();
            syncChevronRotation(item, false);
          } else {
            hidePopover();
            if (currentPopoverOwner) {
              syncChevronRotation(currentPopoverOwner, false);
            }
            popover.show();
            currentPopoverOwner = item;
            syncChevronRotation(item, true);
          }
        }
      } else if (href && href !== "#") {
        window.location.href = href;
      }
    } else {
      // Sidebar is expanded
      if (isCollapseTrigger && href) {
        e.preventDefault();
        const target = document.querySelector(href);
        if (!target) return;

        const isOpen = target.classList.contains("show");

        document.querySelectorAll("#sidebar .collapse.show").forEach((el) => {
          if (el !== target) {
            bootstrap.Collapse.getInstance(el)?.hide();
          }
        });

        const instance =
          bootstrap.Collapse.getInstance(target) ||
          new bootstrap.Collapse(target, { toggle: false });

        if (!isOpen) {
          instance.show();
        } else {
          instance.hide();
        }
      } else if (href && href !== "#") {
        window.location.href = href;
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
      if (currentPopoverOwner) {
        syncChevronRotation(currentPopoverOwner, false);
      }
    }
  });

  // Close popover when clicking outside
  document.addEventListener("click", (e) => {
    const insidePopover = e.target.closest(".popover");
    const insideTrigger = e.target.closest(".sidebar-item");

    if (!insidePopover && !insideTrigger) {
      if (currentPopoverOwner) {
        hidePopover();
        syncChevronRotation(currentPopoverOwner, false);
      }
    }
  });

  // Listener for Bootstrap Collapse events (for expanded sidebar)
  document.querySelectorAll("#sidebar .collapse").forEach((collapseEl) => {
    collapseEl.addEventListener("hidden.bs.collapse", function () {
      const parentSidebarItem = document.querySelector(`[href="#${this.id}"]`);
      if (parentSidebarItem) {
        parentSidebarItem.setAttribute("aria-expanded", "false");
        syncChevronRotation(parentSidebarItem, false);
      }
    });

    collapseEl.addEventListener("shown.bs.collapse", function () {
      const parentSidebarItem = document.querySelector(`[href="#${this.id}"]`);
      if (parentSidebarItem) {
        parentSidebarItem.setAttribute("aria-expanded", "true");
        syncChevronRotation(parentSidebarItem, true);
      }
    });
  });
});
