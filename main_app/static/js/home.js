document.addEventListener('DOMContentLoaded', function() {
    const loginTab = document.querySelector('[data-tab="login"]');
    const signupTab = document.querySelector('[data-tab="signup"]');
    const loginForm = document.getElementById('login-form');
    const signupForm = document.getElementById('signup-form');
    const resetForm = document.getElementById('password-reset-form');

    loginTab.addEventListener('click', function() {
        loginTab.classList.add('active');
        signupTab.classList.remove('active');
        loginForm.classList.remove('hidden');
        signupForm.classList.add('hidden');
        resetForm.classList.add('hidden');
    });

    signupTab.addEventListener('click', function() {
        signupTab.classList.add('active');
        loginTab.classList.remove('active');
        loginForm.classList.add('hidden');
        signupForm.classList.remove('hidden');
        resetForm.classList.add('hidden');
    });

    // Function to show password reset form
    window.showPasswordResetForm = function() {
        loginForm.classList.add('hidden');
        signupForm.classList.add('hidden');
        resetForm.classList.remove('hidden');
    };

    // Function to show login form
    window.showLoginForm = function() {
        loginTab.classList.add('active');
        signupTab.classList.remove('active');
        loginForm.classList.remove('hidden');
        signupForm.classList.add('hidden');
        resetForm.classList.add('hidden');
    };
}); 