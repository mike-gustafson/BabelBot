import asyncio
import base64
import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from translator.services import translate_text
from tts.services import text_to_speech
from googletrans import LANGUAGES
from .forms import TranslationForm, LoginForm, SignupForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import CustomUserCreationForm
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import requests
from django.conf import settings
from .models import Translation

DEFAULT_TARGET_LANGUAGE = "es"
DEFAULT_TEXT = (
    "A long time ago, in a galaxy far, far away. It is a period of civil war. Rebel "
    "spaceships, striking from a hidden base, have won their first victory against the evil "
    "Galactic Empire. During the battle, Rebel spies managed to steal secret plans to the Empire's "
    "ultimate weapon, the DEATH STAR, an armored space station with enough power to destroy an entire "
    "planet. Pursued by the Empire's sinister agents, Princess Leia races home aboard her starship, "
    "custodian of the stolen plans that can save her people and restore freedom to the galaxy..."
)

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
            else:
                text_to_translate = DEFAULT_TEXT
                lang = DEFAULT_TARGET_LANGUAGE
        else:
            text_to_translate = request.GET.get('text', DEFAULT_TEXT)
            lang = request.GET.get('target_language', DEFAULT_TARGET_LANGUAGE)
            form = TranslationForm(initial={
                'text_to_translate': text_to_translate,
                'target_language': lang
            }, selected_language=lang)

        # Translate the text using the specified target language.
        try:
            translated_text = translate_text(text_to_translate, lang)
            # Save the translation to the database
            Translation.objects.create(
                user=request.user if request.user.is_authenticated else None,
                original_text=text_to_translate,
                translated_text=translated_text,
                target_lang=lang
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Translation error: {str(e)}", exc_info=True)
            translated_text = "Translation service is currently unavailable. Please try again later."

        # Check if language is supported for TTS
        tts_message = None
        encoded_audio = None
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
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"TTS error: {str(e)}", exc_info=True)
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
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"General error in translate view: {str(e)}", exc_info=True)
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