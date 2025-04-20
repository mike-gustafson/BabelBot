document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('translation-test-form');
    if (!form) return;

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const submitButton = form.querySelector('button[type="submit"]');
        const resultContainer = document.getElementById('result-container');
        const resultText = document.getElementById('result-text');
        
        submitButton.disabled = true;
        submitButton.textContent = 'Translating...';
        
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
                resultText.innerHTML = `
                    <p><strong>Source Text:</strong> ${data.result.source_text || 'No source text provided'}</p>
                    <p><strong>Translated Text:</strong> ${data.result.translated_text || 'No translation available'}</p>
                    ${data.result.src ? `<p><strong>Detected Language:</strong> ${data.result.src}</p>` : ''}
                `;
                resultContainer.style.display = 'block';
                
                // Show the result for 2 seconds before refreshing
                setTimeout(() => {
                    window.location.reload();
                }, 2000);
            } else {
                resultText.innerHTML = `<p style="color: red;">Error: ${data.error || 'Unknown error occurred'}</p>`;
                resultContainer.style.display = 'block';
            }
        })
        .catch(error => {
            resultText.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
            resultContainer.style.display = 'block';
        })
        .finally(() => {
            submitButton.disabled = false;
            submitButton.textContent = 'Translate';
        });
    });
}); 