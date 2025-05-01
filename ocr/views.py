from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from .services import detect_text
import time
import logging
from functools import wraps

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
@require_POST
@standard_api_view
def perform_ocr(request):
    """
    Handle OCR requests by processing an uploaded image file.
    Returns the extracted text and detected language (if available).
    """
    start_time = time.time()
    
    # Get image from request
    image = request.FILES.get('image')
    if not image:
        return standard_response(
            success=False,
            error='No image provided',
            status=400
        )
    
    # Perform OCR
    ocr_result = detect_text(image.read())
    if not ocr_result:
        return standard_response(
            success=False,
            error='Failed to extract text from image',
            status=400
        )
    
    # Calculate processing time
    processing_time = time.time() - start_time
    
    return standard_response(
        success=True,
        data={
            'text': ocr_result['full_text'],
            'language': ocr_result.get('language', 'unknown'),
            'confidence': ocr_result.get('confidence')
        },
        metadata={
            'processing_time': round(processing_time, 2)
        }
    )
