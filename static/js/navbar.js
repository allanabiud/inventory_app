document.addEventListener("DOMContentLoaded", function () {
  const selectedSearchOption = document.getElementById("selectedSearchOption");
  const hiddenSearchScope = document.getElementById("hiddenSearchScope");
  const dropdownItems = document.querySelectorAll(
    ".dropdown-menu .dropdown-item",
  );
  const searchQueryInput = document.getElementById("searchQueryInput");

  dropdownItems.forEach((item) => {
    item.addEventListener("click", function (e) {
      e.preventDefault();
      const scope = this.getAttribute("data-search-scope");
      const text = this.textContent;

      selectedSearchOption.textContent = text;
      hiddenSearchScope.value = scope;

      // Adjust placeholder based on selection for better UX
      if (scope === "all") {
        searchQueryInput.placeholder = "Perform a global search";
      } else if (scope === "items") {
        searchQueryInput.placeholder = "Search in Items (Name or SKU)";
      } else if (scope === "categories") {
        searchQueryInput.placeholder = "Search in Categories (Name)";
      }

      searchQueryInput.focus(); // Keep focus on the input field
    });
  });

  // Optional: Restore selected option and query from URL on page load
  const urlParams = new URLSearchParams(window.location.search);
  const currentScope = urlParams.get("scope");
  const currentQuery = urlParams.get("q");

  if (currentScope) {
    dropdownItems.forEach((item) => {
      if (item.getAttribute("data-search-scope") === currentScope) {
        selectedSearchOption.textContent = item.textContent;
        hiddenSearchScope.value = currentScope;
        // Update placeholder based on restored scope
        if (currentScope === "all") {
          searchQueryInput.placeholder = "Perform a global search";
        } else if (currentScope === "items") {
          searchQueryInput.placeholder = "Search in Items (Name or SKU)";
        } else if (currentScope === "categories") {
          searchQueryInput.placeholder = "Search in Categories (Name)";
        }
      }
    });
  } else {
    // If no scope is in URL, ensure default placeholder matches 'all'
    searchQueryInput.placeholder = "Perform a global search";
  }

  if (currentQuery) {
    searchQueryInput.value = currentQuery;
  }
});
