from google.cloud import vision
from google.oauth2 import service_account
import os
import json

def get_vision_client():
    """Initialize and return a Google Cloud Vision client using environment variables."""
    try:
        # Get credentials from environment variables
        credentials_dict = {
            "type": os.getenv("GOOGLE_TYPE"),
            "project_id": os.getenv("GOOGLE_PROJECT_ID"),
            "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID"),
            "private_key": os.getenv("GOOGLE_PRIVATE_KEY", "").replace("\\n", "\n"),
            "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "auth_uri": os.getenv("GOOGLE_AUTH_URI"),
            "token_uri": os.getenv("GOOGLE_TOKEN_URI"),
            "auth_provider_x509_cert_url": os.getenv("GOOGLE_AUTH_PROVIDER_X509_CERT_URL"),
            "client_x509_cert_url": os.getenv("GOOGLE_CLIENT_X509_CERT_URL")
        }
        
        # Create credentials from the dictionary
        credentials = service_account.Credentials.from_service_account_info(credentials_dict)
        return vision.ImageAnnotatorClient(credentials=credentials)
    except Exception as e:
        raise Exception(f"Failed to initialize Vision client: {str(e)}")

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

def extract_text_from_image(image_data):
    """
    Extract text from an image using Google Cloud Vision API.
    
    Args:
        image_data (bytes): The image data in bytes format
        
    Returns:
        str: The extracted text from the image
    """
    try:
        result = detect_text(image_data)
        return result['full_text']
    except Exception as e:
        return f"An error occurred while processing the image: {str(e)}" 