document.addEventListener('DOMContentLoaded', function() {
  const menuToggle = document.getElementById('menu-toggle');
  const navLinks = document.querySelector('.nav-links');

  menuToggle.addEventListener('click', function() {
    menuToggle.classList.toggle('active');
    navLinks.classList.toggle('active');
  });

  // Close menu when clicking outside
  document.addEventListener('click', function(event) {
    if (!menuToggle.contains(event.target) && !navLinks.contains(event.target)) {
      menuToggle.classList.remove('active');
      navLinks.classList.remove('active');
    }
  });

  // Close menu when window is resized above mobile breakpoint
  window.addEventListener('resize', function() {
    if (window.innerWidth > 768) {
      menuToggle.classList.remove('active');
      navLinks.classList.remove('active');
    }
  });
});