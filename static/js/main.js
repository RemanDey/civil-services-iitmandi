document.addEventListener("DOMContentLoaded", () => {
    // Mobile Responsive Navbar Toggle
    const menuToggle = document.querySelector(".menu-toggle");
    const navLinks = document.querySelector(".nav-links");

    if (menuToggle && navLinks) {
        menuToggle.addEventListener("click", () => {
            navLinks.classList.toggle("active");
        });
    }

    // Assign active navigation classes contextually
    const currentPath = window.location.pathname;
    const links = document.querySelectorAll(".nav-links a");
    links.forEach(link => {
        if (link.getAttribute("href") === currentPath) {
            link.classList.add("active");
        }
    });
});