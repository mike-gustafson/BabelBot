import os
import logging
from google.cloud import vision
from google.cloud.vision_v1 import types
from functools import wraps

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
        credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if not credentials_path:
            raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable not set")
        
        if not os.path.exists(credentials_path):
            raise ValueError(f"Credentials file not found at {credentials_path}")
        
        return vision.ImageAnnotatorClient()
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