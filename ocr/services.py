import logging
import os
from google.cloud import vision
from django.conf import settings
from google.oauth2 import service_account
from google.api_core.exceptions import GoogleAPIError

logger = logging.getLogger(__name__)

def handle_errors(func):
    """Decorator to handle errors in OCR functions."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            raise
    return wrapper

@handle_errors
def get_vision_client():
    """Initialize and return a Google Cloud Vision client."""
    try:
        # Create credentials dictionary from environment variables
        credentials_dict = {
            "type": settings.GOOGLE_TYPE,
            "project_id": settings.GOOGLE_PROJECT_ID,
            "private_key_id": settings.GOOGLE_PRIVATE_KEY_ID,
            "private_key": settings.GOOGLE_PRIVATE_KEY,
            "client_email": settings.GOOGLE_CLIENT_EMAIL,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "auth_uri": settings.GOOGLE_AUTH_URI,
            "token_uri": settings.GOOGLE_TOKEN_URI,
            "auth_provider_x509_cert_url": settings.GOOGLE_AUTH_PROVIDER_X509_CERT_URL,
            "client_x509_cert_url": settings.GOOGLE_CLIENT_X509_CERT_URL
        }

        # Check if all required fields are present
        required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email', 'client_id']
        missing_fields = [field for field in required_fields if not credentials_dict.get(field)]
        if missing_fields:
            logger.error(f"Missing required Google Cloud credentials: {', '.join(missing_fields)}")
            raise ValueError(f"Missing required Google Cloud credentials: {', '.join(missing_fields)}")

        # Create credentials object directly from the dictionary
        credentials = service_account.Credentials.from_service_account_info(credentials_dict)
        
        # Set the project ID explicitly
        os.environ['GOOGLE_CLOUD_PROJECT'] = settings.GOOGLE_PROJECT_ID
        
        return vision.ImageAnnotatorClient(credentials=credentials)
    except Exception as e:
        logger.error(f"Failed to initialize Vision client: {str(e)}")
        raise Exception(f"Failed to initialize Vision client: {str(e)}")

@handle_errors
def detect_text(image_data):
    """
    Detects text in an image using Google Cloud Vision API.
    """
    try:
        logger.info("Initializing Vision client...")
        client = get_vision_client()
        
        logger.info("Creating image object...")
        image = vision.Image(content=image_data)
        
        logger.info("Sending request to Vision API...")
        response = client.text_detection(image=image)
        
        if response.error.message:
            logger.error(f"Vision API error: {response.error.message}")
            raise GoogleAPIError(response.error.message)
            
        texts = response.text_annotations
        if texts:
            logger.info(f"Successfully detected text. Language: {texts[0].locale if texts[0].locale else 'en'}")
            return {
                'full_text': texts[0].description,
                'language': texts[0].locale if texts[0].locale else 'en'
            }
        logger.warning("No text detected in image")
        return {'full_text': '', 'language': 'en'}
    except Exception as e:
        logger.error(f"Error detecting text: {str(e)}")
        raise Exception(f"Error detecting text: {str(e)}")

def extract_text_from_image(image_data: bytes) -> str:
    """Extract text from an image using Google Cloud Vision API."""
    try:
        logger.info("Starting text extraction...")
        result = detect_text(image_data)
        logger.info("Text extraction completed successfully")
        return result['full_text']
    except Exception as e:
        logger.error(f"Error in extract_text_from_image: {str(e)}")
        return f"An error occurred while processing the image: {str(e)}" 