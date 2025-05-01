import os
import logging
from google.cloud import vision
from google.cloud.vision_v1 import types
from functools import wraps
from django.conf import settings
from google.oauth2 import service_account

logger = logging.getLogger(__name__)

def standard_error_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            logger.error(f"Validation error in {func.__name__}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
            raise
    return wrapper

@standard_error_handler
def get_vision_client():
    """Initialize and return a Google Cloud Vision client."""
    try:
        # Create credentials dictionary from settings
        credentials_dict = {
            "type": settings.GOOGLE_TYPE,
            "project_id": settings.GOOGLE_PROJECT_ID,
            "private_key_id": settings.GOOGLE_PRIVATE_KEY_ID,
            "private_key": settings.GOOGLE_PRIVATE_KEY,
            "client_email": settings.GOOGLE_CLIENT_EMAIL,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{settings.GOOGLE_CLIENT_EMAIL}"
        }

        # Check if all required fields are present
        required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email', 'client_id']
        missing_fields = [field for field in required_fields if not credentials_dict.get(field)]
        if missing_fields:
            raise ValueError(f"Missing required Google Cloud credentials: {', '.join(missing_fields)}")

        # Create credentials object directly from the dictionary
        credentials = service_account.Credentials.from_service_account_info(credentials_dict)
        
        return vision.ImageAnnotatorClient(credentials=credentials)
    except Exception as e:
        logger.error(f"Failed to initialize Vision client: {str(e)}")
        raise

@standard_error_handler
def detect_text(image_content):
    """Detect text in an image using Google Cloud Vision API."""
    try:
        client = get_vision_client()
        image = types.Image(content=image_content)
        response = client.text_detection(image=image)
        
        if response.error.message:
            logger.error(f"API Error: {response.error.message}")
            raise Exception(f"API Error: {response.error.message}")
        
        texts = response.text_annotations
        if not texts:
            return None
        
        full_text = texts[0].description
        language = texts[0].locale if hasattr(texts[0], 'locale') else 'unknown'
        
        return {
            'full_text': full_text,
            'language': language,
            'confidence': response.text_annotations[0].confidence if hasattr(response.text_annotations[0], 'confidence') else None
        }
    except Exception as e:
        logger.error(f"Error detecting text: {str(e)}")
        raise

def extract_text_from_image(image_data: bytes) -> str:
    """Extract text from an image using Google Cloud Vision API."""
    try:
        result = detect_text(image_data)
        return result['full_text']
    except Exception as e:
        return f"An error occurred while processing the image: {str(e)}" 