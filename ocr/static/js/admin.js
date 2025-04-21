document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('ocr-translate-form');
    const imageInput = document.getElementById('image');
    const imagePreview = document.getElementById('image-preview');
    const imagePreviewContainer = document.getElementById('image-preview-container');
    const resultsContainer = document.getElementById('results-container');
    const errorMessage = document.getElementById('error-message');
    
    // Handle image preview
    imageInput.addEventListener('change', function() {
        const file = this.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                imagePreview.src = e.target.result;
                imagePreviewContainer.classList.remove('hidden');
            }
            reader.readAsDataURL(file);
        }
    });
    
    // Handle form submission
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Hide previous results and errors
        resultsContainer.classList.add('hidden');
        errorMessage.classList.add('hidden');
        
        const formData = new FormData(form);
        const submitButton = form.querySelector('button[type="submit"]');
        
        submitButton.disabled = true;
        submitButton.textContent = 'Processing...';
        
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
                // Update results
                document.getElementById('original-text').textContent = data.original_text;
                document.getElementById('original-language').textContent = data.original_language;
                document.getElementById('translated-text').textContent = data.translated_text;
                document.getElementById('translated-language').textContent = data.translated_language;
                document.getElementById('processing-time').textContent = data.processing_time;
                
                // Show results
                resultsContainer.classList.remove('hidden');
                
                // Reload the page to show the new entry in the table
                window.location.reload();
            } else {
                errorMessage.textContent = data.error;
                errorMessage.classList.remove('hidden');
            }
        })
        .catch(error => {
            errorMessage.textContent = 'An error occurred: ' + error.message;
            errorMessage.classList.remove('hidden');
        })
        .finally(() => {
            submitButton.disabled = false;
            submitButton.textContent = 'Process Image';
        });
    });
}); 