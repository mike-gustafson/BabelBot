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
    const radioButtons = document.querySelectorAll('input[name="input-type"]');

    if (!textForm || !ocrForm || !radioButtons) {
        console.error('Required form elements not found');
        return;
    }

    // Handle radio button changes
    radioButtons.forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.value === 'text') {
                textForm.style.display = 'block';
                ocrForm.style.display = 'none';
            } else {
                textForm.style.display = 'none';
                ocrForm.style.display = 'block';
            }
        });
    });

    // Show text form by default
    textForm.style.display = 'block';
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
    const imageInput = document.getElementById('ocr-image-input');
    const ocrStatus = document.getElementById('ocr-status');
    const extractedText = document.querySelector('textarea[name="extracted_text"]');
    const imagePreview = document.getElementById('image-preview');

    if (!imageInput || !ocrStatus || !extractedText) {
        console.error('Required OCR elements not found');
        return;
    }

    imageInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (!file) return;

        // Show image preview
        const reader = new FileReader();
        reader.onload = function(e) {
            imagePreview.src = e.target.result;
            imagePreview.style.display = 'block';
        };
        reader.readAsDataURL(file);

        // Process image with OCR
        const formData = new FormData();
        formData.append('image', file);
        formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);

        fetch('/ocr/process/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            console.log('OCR response:', data); // Debug log
            if (data.success) {
                const text = data.data.full_text || data.data.text || data.data;
                if (text) {
                    extractedText.value = text;
                    document.getElementById('ocr-result').style.display = 'block';
                    ocrStatus.textContent = 'Text extracted successfully';
                    ocrStatus.className = 'success';
                } else {
                    ocrStatus.textContent = 'No text detected in image';
                    ocrStatus.className = 'error';
                }
            } else {
                ocrStatus.textContent = data.error || 'Failed to extract text';
                ocrStatus.className = 'error';
            }
        })
        .catch(error => {
            console.error('Error processing image:', error);
            ocrStatus.textContent = 'Error processing image: ' + error;
            ocrStatus.className = 'error';
        });
    });
}

// Translation form handling
async function handleTranslationResponse(data) {
    const translationResult = document.querySelector('.translated-output');
    const languageInfo = document.querySelector('.language-info');
    const audioContainer = document.getElementById('audio_container');
    const audioPlayer = document.getElementById('audio_player');

    console.log('Translation response:', data); // Debug log

    if (data.success) {
        // Update translation text and language info
        const translatedText = data.translated_text || data.text || data.translation;
        if (!translatedText) {
            console.error('No translation text found in response:', data);
            translationResult.textContent = 'Translation failed: No text returned';
            return;
        }

        translationResult.textContent = translatedText;
        languageInfo.textContent = `Translated from ${data.source_language || data.src || 'auto'} to ${data.target_language || data.dest}`;
        languageInfo.style.display = 'block';

        // Try to generate speech
        try {
            // Get the target language code (first two characters)
            const targetLang = (data.target_language || data.dest || '').substring(0, 2).toLowerCase();
            
            const response = await fetch('/tts/generate/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({
                    text: translatedText,
                    language: targetLang
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const ttsData = await response.json();
            console.log('TTS response:', ttsData); // Debug log

            if (ttsData.success) {
                audioPlayer.src = `data:audio/mp3;base64,${ttsData.encoded_audio}`;
                audioContainer.style.display = 'block';
            } else {
                console.error('TTS error:', ttsData.error);
                audioContainer.style.display = 'none';
            }
        } catch (error) {
            console.error('Error generating speech:', error);
            audioContainer.style.display = 'none';
        }
    } else {
        translationResult.textContent = data.error || 'Translation failed';
        languageInfo.style.display = 'none';
        audioContainer.style.display = 'none';
    }
}

function submitTextForm() {
    const form = document.getElementById('text-translation-form');
    const text = form.querySelector('textarea[name="text_to_translate"]').value;
    const targetLanguage = form.querySelector('select[name="target_language"]').value;
    const resultDiv = document.querySelector('.translated-output');
    const languageInfo = document.querySelector('.language-info');

    if (!text || !targetLanguage) {
        resultDiv.textContent = 'Please provide both text and target language';
        return;
    }

    fetch('/translator/translate/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify({
            text: text,
            target_language: targetLanguage
        })
    })
    .then(response => response.json())
    .then(data => handleTranslationResponse(data))
    .catch(error => {
        console.error('Error:', error);
        resultDiv.textContent = 'Error during translation';
        languageInfo.style.display = 'none';
        document.getElementById('audio_container').style.display = 'none';
    });
}

function submitOCRForm() {
    const form = document.getElementById('ocr-translation-form');
    const extractedText = form.querySelector('textarea[name="extracted_text"]').value;
    const targetLanguage = form.querySelector('select[name="target_language"]').value;
    const resultDiv = document.querySelector('.translated-output');
    const languageInfo = document.querySelector('.language-info');

    if (!extractedText || !targetLanguage) {
        resultDiv.textContent = 'Please provide both text and target language';
        return;
    }

    fetch('/translator/translate/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify({
            text: extractedText,
            target_language: targetLanguage
        })
    })
    .then(response => response.json())
    .then(data => handleTranslationResponse(data))
    .catch(error => {
        console.error('Error:', error);
        resultDiv.textContent = 'Error during translation';
        languageInfo.style.display = 'none';
        document.getElementById('audio_container').style.display = 'none';
    });
}

// Initialize all functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    const textForm = document.getElementById('text-form');
    const ocrForm = document.getElementById('ocr-form');
    const radioButtons = document.querySelectorAll('input[name="input-type"]');
    const imageInput = document.querySelector('input[type="file"]');
    const imagePreview = document.getElementById('image-preview');
    const ocrResult = document.getElementById('ocr-result');
    const extractedText = document.querySelector('#ocr-result textarea');
    const ocrStatus = document.getElementById('ocr-status');
    const uploadLabel = document.querySelector('.upload-label');
    const uploadText = document.querySelector('.upload-text');

    // Handle form toggle
    radioButtons.forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.value === 'text') {
                textForm.style.display = 'block';
                ocrForm.style.display = 'none';
            } else {
                textForm.style.display = 'none';
                ocrForm.style.display = 'block';
            }
        });
    });

    // Handle image selection
    imageInput.addEventListener('change', async function() {
        if (this.files && this.files[0]) {
            // Show preview
            const reader = new FileReader();
            reader.onload = function(e) {
                imagePreview.src = e.target.result;
                imagePreview.style.display = 'block';
                uploadText.textContent = 'Change image';
            };
            reader.readAsDataURL(this.files[0]);

            // Process image automatically
            ocrStatus.textContent = 'Processing image...';
            ocrStatus.className = 'processing';

            try {
                const formData = new FormData();
                formData.append('image', this.files[0]);
                formData.append('form_type', 'ocr');

                const response = await fetch('/ocr/process/', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                });

                const data = await response.json();
                
                if (data.success) {
                    extractedText.value = data.text.full_text;
                    ocrResult.style.display = 'block';
                    ocrStatus.textContent = 'OCR completed successfully!';
                    ocrStatus.className = 'success';
                } else {
                    throw new Error(data.error || 'OCR processing failed');
                }
            } catch (error) {
                ocrStatus.textContent = `Error: ${error.message}`;
                ocrStatus.className = 'error';
            }
        }
    });

    initializeFormToggle();
    initializeImagePreview();
    initializeOCRProcessing();
}); 