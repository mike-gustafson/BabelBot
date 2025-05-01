document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('ocr-test-form');
    if (!form) return;

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const submitButton = form.querySelector('button[type="submit"]');
        const resultContainer = document.getElementById('result-container');
        const resultText = document.getElementById('result-text');
        
        submitButton.disabled = true;
        submitButton.textContent = 'Processing...';
        
        const formData = new FormData(form);
        
        fetch('test/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                resultText.textContent = data.result.full_text;
                resultContainer.style.display = 'block';
                // Reload the page to show the new record
                window.location.reload();
            } else {
                alert('Error: ' + data.error);
            }
        })
        .catch(error => {
            alert('Error: ' + error.message);
        })
        .finally(() => {
            submitButton.disabled = false;
            submitButton.textContent = 'Process Image';
        });
    });
}); 