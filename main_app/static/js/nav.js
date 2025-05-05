document.addEventListener('DOMContentLoaded', function() {
  const menuButton = document.getElementById('mobile-menu-trigger');
  const navContent = document.querySelector('.nav-content');
  const navOverlay = document.getElementById('nav-overlay');
  const closeMenuButton = document.getElementById('close-menu-button');

  function openMenu() {
    navContent.classList.add('nav--active');
    navOverlay.classList.add('active');
  }

  function closeMenu() {
    navContent.classList.remove('nav--active');
    navOverlay.classList.remove('active');
  }

  if (menuButton && navContent && navOverlay && closeMenuButton) {
    menuButton.addEventListener('click', function(e) {
      e.preventDefault();
      openMenu();
    });
    closeMenuButton.addEventListener('click', function(e) {
      e.preventDefault();
      closeMenu();
    });
    navOverlay.addEventListener('click', function(e) {
      e.preventDefault();
      closeMenu();
    });
  }
});