document.addEventListener("DOMContentLoaded", () => {

  const hamburger = document.getElementById("hamburger");
  const mobileMenu = document.getElementById("mobileMenu");

  if (!hamburger || !mobileMenu) return;

  hamburger.addEventListener("click", () => {
      mobileMenu.classList.toggle("active");
  });

  document.querySelectorAll(".mobile-nav-links a")
    .forEach(link =>
      link.addEventListener("click", () =>
        mobileMenu.classList.remove("active")
      )
    );
});
