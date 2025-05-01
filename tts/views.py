from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
import json
from .services import text_to_speech, get_supported_languages, is_language_supported, get_audio_base64

@staff_member_required
def tech_demo(request):
    """Tech demo page for testing TTS functionality."""
    return render(request, 'tts/tech_demo.html')

@csrf_exempt
@require_http_methods(["GET"])
def get_languages(request):
    """Get list of supported languages for TTS."""
    try:
        languages = get_supported_languages()
        return JsonResponse({
            'success': True,
            'languages': languages
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def generate_speech(request):
    """Generate speech from text and return as base64 encoded audio."""
    try:
        data = json.loads(request.body)
        text = data.get('text')
        language = data.get('language', 'en')
        
        if not text:
            return JsonResponse({'error': 'Text is required'}, status=400)
        
        if not is_language_supported(language):
            return JsonResponse({'error': f'Language {language} is not supported'}, status=400)
        
        encoded_audio = get_audio_base64(text, language)
        
        return JsonResponse({
            'success': True,
            'encoded_audio': encoded_audio
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500) 