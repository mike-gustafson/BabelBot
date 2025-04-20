import asyncio
from asgiref.sync import sync_to_async
import base64
import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from translator.services import translate_text, get_available_languages
from tts.services import text_to_speech
from googletrans import LANGUAGES
from .forms import TranslationForm, LoginForm, SignupForm, CustomUserCreationForm
from django.contrib.auth import login, authenticate, get_user
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Translation
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils import timezone
from ocr.services import detect_text

DEFAULT_TARGET_LANGUAGE = "es"
DEFAULT_TEXT = (
    "A long time ago, in a galaxy far, far away. It is a period of civil war. Rebel "
    "spaceships, striking from a hidden base, have won their first victory against the evil "
    "Galactic Empire. During the battle, Rebel spies managed to steal secret plans to the Empire's "
    "ultimate weapon, the DEATH STAR, an armored space station with enough power to destroy an entire "
    "planet. Pursued by the Empire's sinister agents, Princess Leia races home aboard her starship, "
    "custodian of the stolen plans that can save her people and restore freedom to the galaxy..."
)

# Create async versions of database operations
create_translation = sync_to_async(Translation.objects.create)
get_user_async = sync_to_async(get_user)
get_anonymous_user = sync_to_async(lambda: User.objects.get(username='anonymous_translator'))

def build_LANGUAGES_html(selected_language):
    html_content = '<select id="language-select" name="target_language">'
    html_content += '<option value="">Select a language</option>'
    for lang_code, lang_name in LANGUAGES.items():
        selected_attr = ' selected' if lang_code == selected_language else ''
        html_content += f'<option value="{lang_code}"{selected_attr}>{lang_name}</option>'
    html_content += '</select>'
    return html_content

async def translate(request):
    try:
        if request.method == 'POST':
            form = TranslationForm(request.POST)
            if form.is_valid():
                text_to_translate = form.cleaned_data['text_to_translate']
                lang = form.cleaned_data['target_language']
                
                # Translate the text using the specified target language.
                try:
                    translated_text = await translate_text(
                        text_to_translate, 
                        lang,
                        max_retries=3 if 'ON_HEROKU' in os.environ else 1
                    )
                    
                    if translated_text.startswith("Translation service is currently unavailable"):
                        translated_text = "Translation service is currently unavailable. Please try again later."
                    elif translated_text.startswith("Network error"):
                        translated_text = "Network error during translation. Please try again later."
                    else:
                        # Get user in async context
                        user = await get_user_async(request)
                        if not user.is_authenticated:
                            # Use anonymous user if not authenticated
                            user = await get_anonymous_user()
                        
                        # Save the translation to the database using sync_to_async
                        await create_translation(
                            user=user,
                            original_text=text_to_translate,
                            translated_text=translated_text,
                            target_lang=lang
                        )
                        
                except Exception as e:
                    translated_text = "An unexpected error occurred during translation. Please try again later."
            else:
                text_to_translate = DEFAULT_TEXT
                lang = DEFAULT_TARGET_LANGUAGE
                translated_text = ""
        else:
            text_to_translate = request.GET.get('text', DEFAULT_TEXT)
            lang = request.GET.get('target_language', DEFAULT_TARGET_LANGUAGE)
            translated_text = ""
            form = TranslationForm(initial={
                'text_to_translate': text_to_translate,
                'target_language': lang
            }, selected_language=lang)

        # Check if language is supported for TTS
        tts_message = None
        encoded_audio = None
        if translated_text:  # Only generate TTS if we have a translation
            try:
                from gtts.lang import tts_langs
                supported_langs = tts_langs()
                if lang in supported_langs:
                    # Generate TTS audio only for supported languages
                    loop = asyncio.get_running_loop()
                    audio_buffer = await loop.run_in_executor(None, text_to_speech, translated_text, lang)
                    audio_data = audio_buffer.read()
                    encoded_audio = base64.b64encode(audio_data).decode("utf-8")
                else:
                    tts_message = "Text-to-speech is not available for this language."
            except Exception as e:
                tts_message = "Text-to-speech service is currently unavailable."

        context = {
            'form': form,
            'text_to_translate': text_to_translate,
            'translated_text': translated_text,
            'encoded_audio': encoded_audio,
            'tts_message': tts_message,
            'language_dropdown': build_LANGUAGES_html(lang)
        }

        return render(request, 'translate.html', context)
    except Exception as e:
        return render(request, 'translate.html', {
            'form': TranslationForm(),
            'text_to_translate': DEFAULT_TEXT,
            'translated_text': "An error occurred. Please try again.",
            'tts_message': None,
            'language_dropdown': build_LANGUAGES_html(DEFAULT_TARGET_LANGUAGE)
        })

async def translate_ajax(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            form = TranslationForm(data)
            
            if form.is_valid():
                text_to_translate = form.cleaned_data['text_to_translate']
                target_language = form.cleaned_data['target_language']
                
                # Translate the text
                translated_text = translate_text(text_to_translate, target_language)
                
                # Generate TTS audio
                loop = asyncio.get_running_loop()
                audio_buffer = await loop.run_in_executor(None, text_to_speech, translated_text, target_language)
                audio_data = audio_buffer.read()
                encoded_audio = base64.b64encode(audio_data).decode("utf-8")
                
                return JsonResponse({
                    'translated_text': translated_text,
                    'encoded_audio': encoded_audio
                })
            else:
                return JsonResponse({'error': 'Invalid form data', 'errors': form.errors}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            # TODO: Implement actual authentication
            return redirect('home')
    else:
        form = LoginForm()
    
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    # Perform logout logic here
    return HttpResponse("Logout successful")

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            # TODO: Implement actual user creation
            return redirect('login')
    else:
        form = SignupForm()
    
    return render(request, 'signup.html', {'form': form})

def account(request):
    return render(request, 'account.html')

def about(request):
    return render(request, 'about.html')

def home(request):
    return render(request, 'home.html')

class CustomPasswordResetView(PasswordResetView):
    template_name = 'password_reset.html'
    email_template_name = 'password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'password_reset_complete.html'

def index(request):
    languages = get_available_languages()
    return render(request, 'index.html', {'languages': languages})

@csrf_exempt
@require_http_methods(["POST"])
def translate(request):
    try:
        data = json.loads(request.body)
        text = data.get('text')
        target_language = data.get('target_language')
        
        if not text or not target_language:
            return JsonResponse({'error': 'Text and target language are required'}, status=400)
        
        # Translate the text
        result = translate_text(text, target_language)
        
        # Create a translation record
        translation = Translation.objects.create(
            original_text=text,
            translated_text=result['translated_text'],
            source_language=result['src'],
            target_language=target_language
        )
        
        return JsonResponse({
            'success': True,
            'translation': result['translated_text'],
            'source_language': result['src'],
            'translation_id': translation.id
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def ocr(request):
    try:
        if 'image' not in request.FILES:
            return JsonResponse({'error': 'No image provided'}, status=400)
        
        image = request.FILES['image']
        
        # Read the image file into memory
        image_data = image.read()
        
        # Process the image
        result = detect_text(image_data)
        
        return JsonResponse({
            'success': True,
            'text': result['full_text'],
            'language': result['language']
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def tts(request):
    try:
        data = json.loads(request.body)
        text = data.get('text')
        language = data.get('language')
        
        if not text or not language:
            return JsonResponse({'error': 'Text and language are required'}, status=400)
        
        # Generate speech
        audio_data = text_to_speech(text, language)
        
        # Save the audio file
        filename = f"tts_{timezone.now().strftime('%Y%m%d_%H%M%S')}.mp3"
        file_path = os.path.join('tts', filename)
        default_storage.save(file_path, ContentFile(audio_data))
        
        return JsonResponse({
            'success': True,
            'audio_url': f'/media/{file_path}'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)