document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('ocr-test-form');
    const imageInput = document.getElementById('image');
    const imagePreview = document.getElementById('image-preview');
    const imagePreviewContainer = document.getElementById('image-preview-container');
    const resultContainer = document.getElementById('result-container');
    const errorContainer = document.getElementById('error-container');
    const resultText = document.getElementById('result-text');
    const resultLanguage = document.getElementById('result-language');
    const processingTime = document.getElementById('processing-time');
    const saveResultButton = document.getElementById('save-result');

    // Image preview handling
    if (imageInput && imagePreview && imagePreviewContainer) {
        imageInput.addEventListener('change', function(e) {
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    imagePreview.src = e.target.result;
                    imagePreviewContainer.classList.remove('hidden');
                }
                reader.readAsDataURL(this.files[0]);
            }
        });
    }

    // Form submission handling
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Hide previous results and errors
            resultContainer.classList.add('hidden');
            errorContainer.classList.add('hidden');

            const formData = new FormData(this);
            
            fetch(this.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    showError(data.error);
                } else {
                    showResults(data);
                }
            })
            .catch(error => {
                showError('An error occurred while processing the image.');
            });
        });
    }

    // Handle save result button
    saveResultButton.addEventListener('click', function() {
        // The result is already saved on the server side
        this.textContent = 'Saved!';
        this.disabled = true;
        setTimeout(() => {
            this.textContent = 'Save Result';
            this.disabled = false;
        }, 2000);
    });

    function showError(message) {
        const errorContainer = document.getElementById('error-container');
        const errorText = document.getElementById('error-text');
        
        if (errorContainer) {
            errorContainer.classList.remove('hidden');
        }
        if (errorText) {
            errorText.textContent = message;
        }
    }

    function showResults(data) {
        const resultContainer = document.getElementById('result-container');
        const resultText = document.getElementById('result-text');
        const resultLanguage = document.getElementById('result-language');
        const processingTime = document.getElementById('processing-time');

        if (resultContainer) {
            resultContainer.classList.remove('hidden');
        }
        if (resultText) {
            resultText.textContent = data.result.full_text || '';
        }
        if (resultLanguage) {
            resultLanguage.textContent = data.result.language || 'unknown';
        }
        if (processingTime) {
            processingTime.textContent = data.processing_time + ' seconds';
        }
    }

    // Translation Form Handling
    const translationForm = document.getElementById('translation-form');
    if (translationForm) {
        translationForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const submitButton = translationForm.querySelector('button[type="submit"]');
            const resultContainer = document.getElementById('translation-result-container');
            const resultText = document.getElementById('translation-result-text');
            
            submitButton.disabled = true;
            submitButton.textContent = 'Translating...';
            
            const formData = new FormData(translationForm);
            
            fetch('translate/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    resultText.textContent = data.result.translated_text;
                    resultContainer.style.display = 'block';
                } else {
                    alert('Error: ' + data.error);
                }
            })
            .catch(error => {
                alert('Error: ' + error.message);
            })
            .finally(() => {
                submitButton.disabled = false;
                submitButton.textContent = 'Translate';
            });
        });
    }
}); 