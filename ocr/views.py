from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from .services import extract_text_from_image
from functools import wraps
import logging

logger = logging.getLogger(__name__)

def standard_api_view(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        try:
            return func(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    return wrapper

def standard_response(success=True, data=None, error=None, metadata=None):
    response = {
        'success': success,
        'data': data if success else None,
        'error': error if not success else None,
        'metadata': metadata or {}
    }
    return JsonResponse(response)

@staff_member_required
def tech_demo(request):
    """Tech demo page for testing OCR functionality."""
    return render(request, 'ocr/tech_demo.html')

@csrf_exempt
@require_http_methods(["POST"])
@standard_api_view
def perform_ocr(request):
    if 'image' not in request.FILES:
        return standard_response(
            success=False,
            error='No image provided',
            metadata={'status': 400}
        )
            
    try:
        image = request.FILES['image']
        logger.info(f"Processing image: {image.name}")
        
        # Read the image data
        image_data = image.read()
        if not image_data:
            return standard_response(
                success=False,
                error='Empty image data',
                metadata={'status': 400}
            )
            
        # Extract text from the image
        text = extract_text_from_image(image_data)
        
        return standard_response(
            success=True,
            data={'text': text},
            metadata={'status': 200}
        )
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        return standard_response(
            success=False,
            error=str(e),
            metadata={'status': 500}
        )
