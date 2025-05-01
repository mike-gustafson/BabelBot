from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from .services import translate_text, get_available_languages, is_language_supported
from main_app.forms import TranslateFromTextForm
from django.http import JsonResponse
import json
import asyncio

def translate_view(request):
    """View for the main translation page"""
    languages = get_available_languages()
    form = TranslateFromTextForm()
    return render(request, 'translate.html', {
        'form': form,
        'languages': languages,
    })

@staff_member_required
def tech_demo(request):
    """Tech demo page for testing translation functionality."""
    return render(request, 'translator/tech_demo.html')

@require_http_methods(["GET"])
def get_languages(request):
    try:
        languages = get_available_languages()
        return JsonResponse({
            'success': True,
            'languages': languages
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
async def translate_api(request):
    try:
        # Try to get data from JSON first, then fall back to form data
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            data = request.POST
            
        text = data.get('text')
        target_language = data.get('target_language')
        source_language = data.get('source_language')
        
        if not text or not target_language:
            return JsonResponse({
                'error': 'Text and target language are required'
            }, status=400)
            
        result = await translate_text(text, target_language, source_language)
        return JsonResponse({
            'success': True,
            'translation': result['translated_text'],
            'source_language': result['src'],
            'target_language': result['dest'],
            'confidence': result.get('confidence', 1.0)
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
