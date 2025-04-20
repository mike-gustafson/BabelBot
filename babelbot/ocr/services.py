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

def detect_text(image_path):
    """
    Detects text in an image file using Google Cloud Vision API.
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        dict: Dictionary containing the detected text and confidence scores
    """
    try:
        # Initialize the client
        client = get_vision_client()
        
        # Read the image file
        with open(image_path, 'rb') as image_file:
            content = image_file.read()
        
        # Create the image object
        image = vision.Image(content=content)
        
        # Perform text detection
        response = client.text_detection(image=image)
        texts = response.text_annotations
        
        if response.error.message:
            raise Exception(
                '{}\nFor more info on error messages, check: '
                'https://cloud.google.com/apis/design/errors'.format(
                    response.error.message))
        
        # Process the results
        if texts:
            # The first text annotation contains the full text
            full_text = texts[0].description
            
            # Get individual text blocks with their locations
            text_blocks = []
            for text in texts[1:]:  # Skip the first one as it's the full text
                vertices = [(vertex.x, vertex.y) for vertex in text.bounding_poly.vertices]
                text_blocks.append({
                    'text': text.description,
                    'confidence': text.confidence,
                    'bounding_box': vertices
                })
            
            return {
                'full_text': full_text,
                'text_blocks': text_blocks,
                'language': response.text_annotations[0].locale if response.text_annotations[0].locale else 'en'
            }
        else:
            return {
                'full_text': '',
                'text_blocks': [],
                'language': 'en'
            }
            
    except Exception as e:
        raise Exception(f"Error processing image: {str(e)}")

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