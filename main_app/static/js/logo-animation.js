document.addEventListener('DOMContentLoaded', function() {
  const logo = document.getElementById('babelbot-logo');
  
  if (logo) {
    // Click animation - wave and bounce
    logo.addEventListener('click', function(e) {
      // Don't prevent navigation, just add animation
      this.classList.remove('wave-animation', 'bounce-animation');
      this.offsetWidth; // Trigger reflow to restart animation
      this.classList.add('bounce-animation');
      
      // Add a wave sound effect
      const audio = new Audio('/static/audio/boop.mp3');
      audio.volume = 0.2;
      audio.play().catch(e => {
        // Silent error if autoplay is blocked
        console.log('Audio play prevented by browser policy');
      });
    });
    
    // Random animations on page load
    setTimeout(() => {
      logo.classList.add('wave-animation');
      
      // Set up random animations every 30-60 seconds
      setInterval(() => {
        // Remove existing animations
        logo.classList.remove('wave-animation', 'bounce-animation');
        logo.offsetWidth; // Trigger reflow
        
        // Choose random animation
        const animations = ['wave-animation', 'bounce-animation'];
        const randomAnimation = animations[Math.floor(Math.random() * animations.length)];
        
        logo.classList.add(randomAnimation);
      }, Math.random() * 30000 + 30000); // Random time between 30-60 seconds
    }, 2000); // Initial delay of 2 seconds after page load
  }

  // Footer bot bounce on click
  const footerBot = document.querySelector('.footer-bot');
  if (footerBot) {
    footerBot.addEventListener('click', function() {
      footerBot.classList.remove('bounce'); // reset if already bouncing
      void footerBot.offsetWidth; // force reflow
      footerBot.classList.add('bounce');
    });
    footerBot.addEventListener('animationend', function() {
      footerBot.classList.remove('bounce');
    });
  }
}); 