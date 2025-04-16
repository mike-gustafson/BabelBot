import asyncio
import base64
import json
import os
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
import logging
from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)

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
            logger.info(f"Starting translation for text: {text_to_translate[:50]}...")
            
            # Check if we're on Heroku
            is_heroku = 'ON_HEROKU' in os.environ
            if is_heroku:
                logger.info("Running on Heroku - using extended timeout and retries")
            
            translated_text = await translate_text(
                text_to_translate, 
                lang,
                max_retries=3 if is_heroku else 1
            )
            
            if translated_text.startswith("Translation service is currently unavailable"):
                logger.warning("Translation service returned error message")
            elif translated_text.startswith("Network error"):
                logger.warning("Network error during translation")
            else:
                # Save the translation to the database using sync_to_async
                logger.info("Saving translation to database")
                await create_translation(
                    user=request.user if request.user.is_authenticated else None,
                    original_text=text_to_translate,
                    translated_text=translated_text,
                    target_lang=lang
                )
                logger.info("Translation saved to database")
                
        except Exception as e:
            logger.error(f"Translation error in view: {str(e)}", exc_info=True)
            logger.error(f"Error type: {type(e)}")
            logger.error(f"Error args: {e.args}")
            translated_text = "An unexpected error occurred during translation. Please try again later."

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