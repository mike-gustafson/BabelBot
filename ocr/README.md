# Django OCR Module

A modular Optical Character Recognition (OCR) component for Django projects that extracts text from images using Google Cloud Vision API.

## About

This module provides a simple way to add OCR functionality to your Django applications. It uses Google Cloud Vision API to extract text from images and can be integrated with the translator module for multilingual text extraction. The module is designed to be easily integrated into any Django project and can be used either as a standalone service or alongside other features like translation.

## How to Use

### Installation

1. Install the required package:
```bash
pip install google-cloud-vision
```

2. Add 'ocr' to your Django project's `INSTALLED_APPS` in `settings.py`:
```python
INSTALLED_APPS = [
    ...
    'ocr',
]
```

3. Include the OCR URLs in your project's `urls.py`:
```python
urlpatterns = [
    ...
    path('ocr/', include('ocr.urls')),
]
```

4. Set up Google Cloud credentials:
   - Create a service account in Google Cloud Console
   - Download the JSON key file
   - Set the environment variable:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/credentials.json"
   ```

### Basic Usage

#### As a Service
```python
from ocr.services import detect_text

# Extract text from an image
with open('image.jpg', 'rb') as image_file:
    image_data = image_file.read()
    result = detect_text(image_data)
    print(result['full_text'])  # Extracted text
    print(result['language'])   # Detected language
```

#### Using the API Endpoints

1. Extract text from an image:
```http
POST /ocr/api/ocr/
Content-Type: multipart/form-data

image: <image_file>
```

2. Extract and translate text:
```http
POST /ocr/api/ocr-translate/
Content-Type: multipart/form-data

image: <image_file>
target_language: <language_code>
```

## How It Works

### Core Components

1. **Services (`services.py`)**
   - `detect_text()`: Extracts text from an image using Google Cloud Vision API
   - `extract_text_from_image()`: Wrapper function for text extraction with error handling
   - `get_vision_client()`: Initializes the Google Cloud Vision client

2. **Views (`views.py`)**
   - `tech_demo()`: Staff-only tech demo page for testing OCR
   - `process_image()`: Handles base64-encoded image processing
   - `perform_ocr()`: API endpoint for text extraction
   - `perform_ocr_translate()`: API endpoint for text extraction and translation

3. **URLs (`urls.py`)**
   - Maps the API endpoints to URLs

### Example Integration

Here's how you might use the OCR module in a document processing app:

```python
from ocr.services import detect_text
from translator.services import translate_text

async def process_document(image_data, target_language):
    # First extract text from the image
    ocr_result = detect_text(image_data)
    if not ocr_result or 'full_text' not in ocr_result:
        return {'error': 'Failed to extract text from image'}
    
    # Then translate the text if needed
    if target_language != 'detect':
        translated_result = await translate_text(ocr_result['full_text'], target_language)
        return {
            'original_text': ocr_result['full_text'],
            'translated_text': translated_result['translated_text'],
            'language': target_language
        }
    
    return {
        'text': ocr_result['full_text'],
        'language': ocr_result.get('language', 'unknown')
    }
```

### Best Practices

1. Always validate image data before processing
2. Handle image size and format restrictions
3. Consider rate limiting for production use
4. Use the tech demo for testing and debugging
5. Implement proper error handling and logging

## Limitations

- Requires an internet connection (uses Google Cloud Vision API)
- Requires Google Cloud credentials
- Has size and format restrictions for images
- May have rate limits in production
- Tech demo requires staff/admin privileges

## Error Handling
The module implements standardized error handling:
- Validation errors (400)
- API errors (500)
- Detailed error messages
- Consistent logging

## Attribution
This module uses the Google Cloud Vision API for OCR capabilities.

## License
Same as the main project.

---

*This documentation was generated by Cursor AI with prompting and guidance from Mike Gustafson. The content is designed to be accessible to bootcamp students while providing comprehensive information about the OCR module's functionality and usage.* 