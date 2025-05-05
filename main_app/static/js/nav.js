document.addEventListener('DOMContentLoaded', function() {
  const menuButton = document.getElementById('mobile-menu-trigger');
  const navContent = document.querySelector('.nav-content');

  if (menuButton && navContent) {
    menuButton.addEventListener('click', function(e) {
      e.preventDefault();
      navContent.classList.toggle('nav--active');
    });
  }
});