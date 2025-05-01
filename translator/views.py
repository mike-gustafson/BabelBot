from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from .services import translate_text, get_available_languages, is_language_supported
from main_app.forms import TranslationForm
from django.http import JsonResponse
import json
import logging

logger = logging.getLogger(__name__)

def translate_view(request):
    """View for the main translation page"""
    languages = get_available_languages()
    form = TranslationForm()
    return render(request, 'translate.html', {
        'form': form,
        'languages': languages,
    })

@staff_member_required
def tech_demo(request):
    """Tech demo page for testing translation functionality."""
    return render(request, 'translator/tech_demo.html')

@csrf_exempt
@require_http_methods(["GET"])
def get_languages(request):
    """Get list of supported languages for translation."""
    try:
        languages = get_available_languages()
        return JsonResponse({
            'success': True,
            'languages': languages
        })
    except Exception as e:
        logger.error(f"Error getting languages: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
async def translate_api(request):
    """API endpoint for translation with improved error handling."""
    try:
        data = json.loads(request.body)
        text = data.get('text')
        target_language = data.get('target_language')
        source_language = data.get('source_language')
        
        if not text:
            return JsonResponse({'error': 'Text is required'}, status=400)
            
        if not target_language:
            return JsonResponse({'error': 'Target language is required'}, status=400)
            
        if not is_language_supported(target_language):
            return JsonResponse({'error': f'Language {target_language} is not supported'}, status=400)
            
        if source_language and not is_language_supported(source_language):
            return JsonResponse({'error': f'Source language {source_language} is not supported'}, status=400)
        
        try:
            # Translate the text
            result = await translate_text(text, target_language, source_language)
            
            return JsonResponse({
                'success': True,
                'translation': result['translated_text'],
                'source_language': result['src'],
                'target_language': result['dest'],
                'confidence': result['confidence']
            })
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Request error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
