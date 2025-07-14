document.addEventListener("DOMContentLoaded", () => {
  // Animate all elements with class .count-up
  const counters = document.querySelectorAll(".count-up");

  counters.forEach((counter) => {
    const target = +counter.getAttribute("data-target");
    const duration = 800;
    const stepTime = Math.max(Math.floor(duration / target), 10);
    let current = 0;

    const increment = () => {
      current += 1;
      counter.textContent = current;
      if (current < target) {
        setTimeout(increment, stepTime);
      } else {
        counter.textContent = target;
      }
    };

    increment();
  });

  // Animate #totalItemsOverlay
  const totalItemsOverlay = document.getElementById("totalItemsOverlay");
  const totalCountSpan = document.getElementById("totalItemsCount");
  if (totalItemsOverlay && totalCountSpan) {
    const target = +totalItemsOverlay.getAttribute("data-target");
    const duration = 800;
    const stepTime = Math.max(Math.floor(duration / target), 10);
    let current = 0;

    const increment = () => {
      current += 1;
      totalCountSpan.textContent = current;
      if (current < target) {
        setTimeout(increment, stepTime);
      } else {
        totalCountSpan.textContent = target;
      }
    };

    increment();
  }
});
