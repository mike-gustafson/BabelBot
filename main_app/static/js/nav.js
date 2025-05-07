document.addEventListener('DOMContentLoaded', function() {
  const menuButton = document.getElementById('mobile-menu-trigger');
  const navContent = document.querySelector('.nav-content');
  const navOverlay = document.getElementById('nav-overlay');

  function toggleMenu() {
    navContent.classList.toggle('nav--active');
    navOverlay.classList.toggle('active');
  }

  if (menuButton && navContent && navOverlay) {
    menuButton.addEventListener('click', function(e) {
      e.preventDefault();
      toggleMenu();
    });
    navOverlay.addEventListener('click', function(e) {
      e.preventDefault();
      toggleMenu();
    });
  }
});