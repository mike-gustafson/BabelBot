document.addEventListener('DOMContentLoaded', function() {
  const menuToggle = document.getElementById('menu-toggle');
  const navLinks = document.querySelector('.nav-links');

  menuToggle.addEventListener('click', function() {
    menuToggle.classList.toggle('active');
    navLinks.classList.toggle('nav-visible');
  });

  // Close menu when clicking outside
  document.addEventListener('click', function(event) {
    const isClickInside = navLinks.contains(event.target) || menuToggle.contains(event.target);
    
    if (!isClickInside && navLinks.classList.contains('nav-visible')) {
      menuToggle.classList.remove('active');
      navLinks.classList.remove('nav-visible');
    }
  });

  // Close menu when window is resized to desktop size
  window.addEventListener('resize', function() {
    if (window.innerWidth > 768) {
      menuToggle.classList.remove('active');
      navLinks.classList.remove('nav-visible');
    }
  });
});