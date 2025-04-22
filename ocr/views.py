from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .services import extract_text_from_image
from translator.services import translate_text
import json
import base64
from PIL import Image
import io
import time
from .services import detect_text
from main_app.models import Translation
import asyncio
from django.contrib.auth import get_user, get_user_model
from asgiref.sync import sync_to_async

# Create your views here.

def validate_image_data(image_data):
    """
    Validate the image data before processing.
    
    Args:
        image_data (str): Base64 encoded image data
        
    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    try:
        # Check if the data is properly formatted
        if not image_data.startswith('data:image/'):
            return False, "Invalid image format. Please upload a valid image file."
            
        # Extract the base64 part
        image_bytes = base64.b64decode(image_data.split(',')[1])
        
        # Try to open the image to validate it
        image = Image.open(io.BytesIO(image_bytes))
        
        # Check image size (max 5MB for Heroku)
        if len(image_bytes) > 5 * 1024 * 1024:
            return False, "Image is too large. Maximum size is 5MB."
            
        # Check image dimensions
        if image.width > 4096 or image.height > 4096:
            return False, "Image dimensions are too large. Maximum size is 4096x4096 pixels."
            
        # Convert to RGB if necessary (some image formats like PNG might have alpha channel)
        if image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info):
            image = image.convert('RGB')
            
        # Save the image in a memory-efficient format
        output = io.BytesIO()
        image.save(output, format='JPEG', quality=85)
        processed_image = output.getvalue()
        
        return True, processed_image
        
    except Exception as e:
        return False, "Invalid image file. Please try another image."

@csrf_exempt
@require_POST
async def process_image(request):
    """
    Process an uploaded image, extract text using OCR, and translate it.
    """
    start_time = time.time()
    try:
        # Parse the request data
        data = json.loads(request.body)
        image_data = data.get('image')
        target_language = data.get('target_language', 'en')
        
        if not image_data:
            return JsonResponse({
                'error': 'No image data provided'
            }, status=400)
            
        # Validate the image
        is_valid, result = validate_image_data(image_data)
        if not is_valid:
            return JsonResponse({
                'error': result
            }, status=400)
            
        # Extract text from image
        extracted_text = extract_text_from_image(result)
        
        if extracted_text.startswith("An error occurred"):
            return JsonResponse({
                'error': extracted_text
            }, status=400)
            
        # Translate the extracted text
        translated_text = await translate_text(extracted_text, target_language)
        
        processing_time = time.time() - start_time
        
        return JsonResponse({
            'extracted_text': extracted_text,
            'translated_text': translated_text,
            'processing_time': f"{processing_time:.2f}s"
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid request data format'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': 'An unexpected error occurred while processing the image'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def perform_ocr(request):
    """Handle OCR requests"""
    try:
        start_time = time.time()
        
        # Get image from request
        image = request.FILES.get('image')
        if not image:
            return JsonResponse({'error': 'No image provided'}, status=400)
        
        # Perform OCR
        ocr_result = detect_text(image.read())
        if not ocr_result or 'full_text' not in ocr_result:
            return JsonResponse({'error': 'Failed to extract text from image'}, status=400)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Save result
        ocr = OCR.objects.create(
            result=ocr_result
        )
        
        return JsonResponse({
            'id': ocr.id,
            'text': ocr_result['full_text'],
            'language': ocr_result.get('language', 'unknown'),
            'processing_time': round(processing_time, 2)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Create async versions of database operations
get_user_async = sync_to_async(get_user)
create_user = sync_to_async(get_user_model().objects.create_user)

async def get_or_create_anonymous_user():
    User = get_user_model()
    try:
        return await sync_to_async(User.objects.get)(username='anonymous_translator')
    except User.DoesNotExist:
        return await create_user(username='anonymous_translator', password='password123')

create_translation = sync_to_async(Translation.objects.create)

@csrf_exempt
@require_http_methods(["POST"])
def perform_ocr_translate(request):
    """Handle OCR and translation requests"""
    try:
        start_time = time.time()
        
        # Get image and target language
        image = request.FILES.get('image')
        target_language = request.POST.get('target_language')
        
        if not image or not target_language:
            return JsonResponse({'error': 'Image and target language are required'}, status=400)
        
        # Read image data into memory
        image_data = image.read()
        
        # Perform OCR
        ocr_result = detect_text(image_data)
        if not ocr_result or 'full_text' not in ocr_result:
            return JsonResponse({'error': 'Failed to extract text from image'}, status=400)
        
        # Get user in async context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            user = loop.run_until_complete(get_user_async(request))
            if not user.is_authenticated:
                user = loop.run_until_complete(get_or_create_anonymous_user())
            
            # If target language is 'detect', just return the OCR result
            if target_language == 'detect':
                processing_time = time.time() - start_time
                
                # Save to Translation model
                translation = loop.run_until_complete(create_translation(
                    user=user,
                    original_text=ocr_result['full_text'],
                    translated_text=ocr_result['full_text'],  # No translation, so same as original
                    target_lang=ocr_result.get('language', 'unknown'),
                    request_type='ocr'
                ))
                
                return JsonResponse({
                    'id': translation.id,
                    'original_text': ocr_result['full_text'],
                    'detected_language': ocr_result.get('language', 'unknown'),
                    'processing_time': round(processing_time, 2)
                })
            
            # Otherwise, translate the text
            translation_result = loop.run_until_complete(translate_text(ocr_result['full_text'], target_language))
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Save to Translation model
            translation = loop.run_until_complete(create_translation(
                user=user,
                original_text=ocr_result['full_text'],
                translated_text=translation_result.get('translated_text', ''),
                target_lang=target_language,
                request_type='ocr'
            ))
            
            return JsonResponse({
                'id': translation.id,
                'original_text': ocr_result['full_text'],
                'detected_language': ocr_result.get('language', 'unknown'),
                'translated_text': translation_result.get('translated_text', ''),
                'target_language': target_language,
                'processing_time': round(processing_time, 2)
            })
        finally:
            loop.close()
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
