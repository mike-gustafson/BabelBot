// Admin JavaScript functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize any admin-specific functionality here
    console.log('Admin JavaScript loaded');

    // Example: Add click handlers for admin buttons
    const adminButtons = document.querySelectorAll('.admin-button');
    adminButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            console.log('Admin button clicked:', this.textContent);
        });
    });

    // Example: Add form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;

            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('error');
                } else {
                    field.classList.remove('error');
                }
            });

            if (!isValid) {
                e.preventDefault();
                alert('Please fill in all required fields');
            }
        });
    });

    // Example: Add dynamic table functionality
    const tables = document.querySelectorAll('.admin-table');
    tables.forEach(table => {
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(row => {
            row.addEventListener('click', function() {
                this.classList.toggle('selected');
            });
        });
    });
}); 