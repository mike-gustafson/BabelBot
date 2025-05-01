// Utility functions
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Form toggle functionality
function initializeFormToggle() {
    const textForm = document.getElementById('text-form');
    const ocrForm = document.getElementById('ocr-form');
    const textToggle = document.getElementById('text-toggle');
    const ocrToggle = document.getElementById('ocr-toggle');

    if (!textForm || !ocrForm || !textToggle || !ocrToggle) {
        console.error('Required form elements not found');
        return;
    }

    textToggle.addEventListener('click', function() {
        textForm.classList.add('active');
        ocrForm.classList.remove('active');
        textToggle.classList.add('active');
        ocrToggle.classList.remove('active');
    });

    ocrToggle.addEventListener('click', function() {
        ocrForm.classList.add('active');
        textForm.classList.remove('active');
        ocrToggle.classList.add('active');
        textToggle.classList.remove('active');
    });
}

// Image preview functionality
function initializeImagePreview() {
    const imagePreview = document.getElementById('image-preview');
    const imageInput = document.getElementById('ocr-image-input');
    const processButton = document.getElementById('process-button');

    if (!imagePreview || !imageInput || !processButton) {
        console.error('Required image preview elements not found');
        return;
    }

    imageInput.addEventListener('change', function() {
        const file = this.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                imagePreview.src = e.target.result;
                imagePreview.style.display = 'block';
                processButton.disabled = false;
            };
            reader.readAsDataURL(file);
        }
    });
}

// OCR processing functionality
function initializeOCRProcessing() {
    const processButton = document.getElementById('process-button');
    const imageInput = document.getElementById('ocr-image-input');
    const ocrStatus = document.getElementById('ocr-status');
    const originalText = document.getElementById('original_text');
    const textToggle = document.getElementById('text-toggle');

    if (!processButton || !imageInput || !ocrStatus || !originalText || !textToggle) {
        console.error('Required OCR processing elements not found');
        return;
    }

    processButton.addEventListener('click', function() {
        const formData = new FormData();
        formData.append('image', imageInput.files[0]);

        fetch('/ocr/process/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                ocrStatus.textContent = 'Error: ' + data.error;
                ocrStatus.className = 'error';
            } else {
                ocrStatus.textContent = 'OCR completed successfully!';
                ocrStatus.className = 'success';
                originalText.value = data.full_text;
                // Switch to text form and trigger translation
                textToggle.click();
                // Trigger form submission
                document.querySelector('form').submit();
            }
        })
        .catch(error => {
            ocrStatus.textContent = 'Error processing image: ' + error;
            ocrStatus.className = 'error';
        });
    });
}

// Initialize all functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeFormToggle();
    initializeImagePreview();
    initializeOCRProcessing();
}); 