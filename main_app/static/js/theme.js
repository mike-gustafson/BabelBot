document.addEventListener('DOMContentLoaded', () => {
  const themeToggle = document.getElementById('theme-toggle');
  const themeIcon = document.querySelector('.theme-icon');
  const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');

  // Re-enable transitions after initial load
  document.body.style.transition = 'background-color 0.3s ease, color 0.3s ease';
  document.querySelectorAll('*').forEach(el => {
    el.style.transition = 'all 0.3s ease';
  });

  // Check for saved theme preference or use system preference
  const currentTheme = localStorage.getItem('theme') || 
                      (prefersDarkScheme.matches ? 'dark' : 'light');
  
  // Apply the saved theme
  if (currentTheme === 'dark') {
    document.documentElement.setAttribute('data-theme', 'dark');
    themeIcon.textContent = '☀️';
  }

  // Handle theme toggle
  themeToggle.addEventListener('click', () => {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    themeIcon.textContent = newTheme === 'dark' ? '☀️' : '🌙';
  });

  // Listen for system theme changes
  prefersDarkScheme.addEventListener('change', (e) => {
    if (!localStorage.getItem('theme')) {
      const newTheme = e.matches ? 'dark' : 'light';
      document.documentElement.setAttribute('data-theme', newTheme);
      themeIcon.textContent = newTheme === 'dark' ? '☀️' : '🌙';
    }
  });
}); 