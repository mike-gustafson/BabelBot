import os
import json
from google.cloud import vision
from google.oauth2 import service_account

def get_vision_client():
    """Initialize and return a Google Cloud Vision client."""
    # Get credentials from environment variables
    credentials_dict = {
        "type": os.getenv("GOOGLE_TYPE"),
        "project_id": os.getenv("GOOGLE_PROJECT_ID"),
        "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID"),
        "private_key": os.getenv("GOOGLE_PRIVATE_KEY").replace("\\n", "\n"),
        "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "auth_uri": os.getenv("GOOGLE_AUTH_URI"),
        "token_uri": os.getenv("GOOGLE_TOKEN_URI"),
        "auth_provider_x509_cert_url": os.getenv("GOOGLE_AUTH_PROVIDER_X509_CERT_URL"),
        "client_x509_cert_url": os.getenv("GOOGLE_CLIENT_X509_CERT_URL")
    }
    
    credentials = service_account.Credentials.from_service_account_info(credentials_dict)
    return vision.ImageAnnotatorClient(credentials=credentials)

def detect_text(image_data):
    """Detect text in an image using Google Cloud Vision API."""
    try:
        # Initialize the client
        client = vision.ImageAnnotatorClient()
        
        # Create an image object
        image = vision.Image(content=image_data)
        
        # Perform text detection
        response = client.text_detection(image=image)
        texts = response.text_annotations
        
        if response.error.message:
            raise Exception(f'{response.error.message}')
        
        if not texts:
            return {
                'full_text': '',
                'language': 'unknown',
                'confidence': 0
            }
        
        # Get the full text and language
        full_text = texts[0].description
        language = texts[0].locale if hasattr(texts[0], 'locale') else 'unknown'
        
        return {
            'full_text': full_text,
            'language': language,
            'confidence': response.text_annotations[0].confidence if response.text_annotations else 0
        }
        
    except Exception as e:
        return {
            'error': str(e),
            'full_text': '',
            'language': 'unknown',
            'confidence': 0
        }

def detect_language(text):
    """
    Detects the language of the given text using Google Cloud Vision API.
    
    Args:
        text (str): Text to detect language for
        
    Returns:
        str: Detected language code
    """
    try:
        client = get_vision_client()
        image = vision.Image(content=text.encode('utf-8'))
        response = client.text_detection(image=image)
        
        if response.error.message:
            raise Exception(
                '{}\nFor more info on error messages, check: '
                'https://cloud.google.com/apis/design/errors'.format(
                    response.error.message))
        
        if response.text_annotations:
            return response.text_annotations[0].locale
        return 'en'  # Default to English if detection fails
        
    except Exception as e:
        raise Exception(f"Error detecting language: {str(e)}") 