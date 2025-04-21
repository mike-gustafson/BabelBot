from google.cloud import vision
from google.oauth2 import service_account
from typing import Dict, Union
import os

def get_vision_client() -> vision.ImageAnnotatorClient:
    """Initialize Google Cloud Vision client using environment variables."""
    try:
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
        
        # Validate required credentials
        missing_credentials = [key for key, value in credentials_dict.items() if not value]
        if missing_credentials:
            raise ValueError(f"Missing required credentials: {', '.join(missing_credentials)}")
        
        credentials = service_account.Credentials.from_service_account_info(credentials_dict)
        return vision.ImageAnnotatorClient(credentials=credentials)
    except Exception as e:
        raise Exception(f"Failed to initialize Vision client: {str(e)}")

def detect_text(image_data: bytes) -> Dict[str, Union[str, float]]:
    """Detect text in an image using Google Cloud Vision API."""
    try:
        client = get_vision_client()
        image = vision.Image(content=image_data)
        
        # Perform text detection
        response = client.text_detection(image=image)
        
        if response.error.message:
            raise Exception(f'Error from Vision API: {response.error.message}')
        
        texts = response.text_annotations
        if not texts:
            return {
                'full_text': '',
                'language': 'unknown',
                'confidence': 0.0
            }
        
        # Get the full text (first annotation contains all text)
        full_text = texts[0].description
        
        # Get language detection
        language_response = client.document_text_detection(image=image)
        language = (
            language_response.text_annotations[0].locale 
            if language_response.text_annotations 
            else 'unknown'
        )
        
        return {
            'full_text': full_text,
            'language': language,
            'confidence': 1.0  # Vision API doesn't provide confidence scores for text detection
        }
        
    except Exception as e:
        raise Exception(f'Error processing image: {str(e)}')

def extract_text_from_image(image_data: bytes) -> str:
    """Extract text from an image using Google Cloud Vision API."""
    try:
        result = detect_text(image_data)
        return result['full_text']
    except Exception as e:
        return f"An error occurred while processing the image: {str(e)}" 