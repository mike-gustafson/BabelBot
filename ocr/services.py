from google.cloud import vision
from google.oauth2 import service_account
from google.api_core.exceptions import GoogleAPIError, DeadlineExceeded
import io
import logging
import os
import json
import tempfile
import time

logger = logging.getLogger(__name__)

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

def detect_text(image_data, max_retries=3, timeout=30):
    """
    Detect text in an image using Google Cloud Vision API.
    
    Args:
        image_data (bytes): The image data in bytes format
        max_retries (int): Maximum number of retry attempts
        timeout (int): Timeout in seconds for the API call
        
    Returns:
        dict: Dictionary containing the detected text, language, and confidence
    """
    for attempt in range(max_retries):
        try:
            # Initialize the Vision client
            client = get_vision_client()
            
            # Create image object directly from bytes
            image = vision.Image(content=image_data)
            
            # Perform text detection with timeout
            start_time = time.time()
            response = client.text_detection(
                image=image,
                timeout=timeout
            )
            
            if response.error.message:
                raise Exception(f'Vision API error: {response.error.message}')
            
            # Process the results
            texts = response.text_annotations
            if texts:
                full_text = texts[0].description
                
                # Detect language
                response = client.document_text_detection(
                    image=image,
                    timeout=timeout
                )
                language = response.text_annotations[0].locale if response.text_annotations else "unknown"
                
                result = {
                    'full_text': full_text,
                    'language': language,
                    'confidence': response.text_annotations[0].confidence if response.text_annotations else None
                }
                return result
            else:
                return {'full_text': '', 'language': 'unknown', 'confidence': None}
                
        except DeadlineExceeded:
            if attempt < max_retries - 1:
                time.sleep(1)  # Wait before retrying
                continue
            raise Exception("OCR request timed out. Please try again.")
        except GoogleAPIError as e:
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
            raise Exception(f"Google Cloud Vision API error: {str(e)}")
        except Exception as e:
            raise Exception(f"Error processing image: {str(e)}")

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