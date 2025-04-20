from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .services import translate_text, get_available_languages
from main_app.forms import TranslationForm
from django.http import JsonResponse
import json

def translate_view(request):
    """View for the main translation page"""
    languages = get_available_languages()
    form = TranslationForm()
    return render(request, 'translate.html', {
        'form': form,
        'languages': languages,
    })

@csrf_exempt
@require_http_methods(["POST"])
async def translate_api(request):
    """API endpoint for translation"""
    try:
        data = json.loads(request.body)
        text = data.get('text')
        target_language = data.get('target_language')
        
        if not text or not target_language:
            return JsonResponse({'error': 'Text and target language are required'}, status=400)
        
        # Translate the text
        result = await translate_text(text, target_language)
        
        return JsonResponse({
            'success': True,
            'translation': result['translated_text'],
            'source_language': result['src'],
            'target_language': result['dest']
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
