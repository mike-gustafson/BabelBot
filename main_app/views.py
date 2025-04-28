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
from django.contrib.auth import login, authenticate, logout, get_user
from django.contrib.auth.models import User
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
from django.contrib.auth.decorators import login_required

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

def build_LANGUAGES_html(selected_language):
    html_content = '<select id="language-select" name="target_language">'
    html_content += '<option value="">Select a language</option>'
    for lang_code, lang_name in LANGUAGES.items():
        selected_attr = ' selected' if lang_code == selected_language else ''
        html_content += f'<option value="{lang_code}"{selected_attr}>{lang_name}</option>'
    html_content += '</select>'
    return html_content

async def translate_view(request):
    try:
        # Wrap session access in sync_to_async
        text_to_translate = await sync_to_async(lambda: request.session.get('text_to_translate', DEFAULT_TEXT))()
        lang = await sync_to_async(lambda: request.session.get('target_language', DEFAULT_TARGET_LANGUAGE))()
        
        # Create form instance asynchronously
        form = await sync_to_async(TranslationForm)()
        
        # Build language dropdown asynchronously
        language_dropdown = await sync_to_async(build_LANGUAGES_html)(lang)
        
        return await sync_to_async(render)(request, 'translate.html', {
            'form': form,
            'text_to_translate': text_to_translate,
            'translated_text': "",
            'language_dropdown': language_dropdown
        })
        
    except Exception as e:
        # Create form instance asynchronously for error case
        form = await sync_to_async(TranslationForm)()
        
        # Build language dropdown asynchronously for error case
        language_dropdown = await sync_to_async(build_LANGUAGES_html)(DEFAULT_TARGET_LANGUAGE)
        
        return await sync_to_async(render)(request, 'translate.html', {
            'form': form,
            'text_to_translate': DEFAULT_TEXT,
            'translated_text': "An error occurred. Please try again.",
            'language_dropdown': language_dropdown
        })

@csrf_exempt
@require_http_methods(["POST"])
async def translate_ajax(request):
    try:
        data = json.loads(request.body)
        text_to_translate = data.get('text_to_translate')
        target_language = data.get('target_language')
        
        if not text_to_translate or not target_language:
            return JsonResponse({
                'error': 'Text and target language are required'
            }, status=400)
        
        # Translate the text
        result = await translate_text(text_to_translate, target_language)
        
        # Check if user is authenticated using sync_to_async
        is_authenticated = await sync_to_async(lambda: request.user.is_authenticated)()
        
        # Save the translation to the database if user is authenticated
        if is_authenticated:
            user = await sync_to_async(lambda: request.user)()
            await create_translation(
                user=user,
                original_text=text_to_translate,
                translated_text=result['translated_text'],
                target_lang=target_language
            )
        
        # Generate TTS if the language is supported
        encoded_audio = None
        try:
            from gtts.lang import tts_langs
            supported_langs = tts_langs()
            if target_language in supported_langs:
                loop = asyncio.get_running_loop()
                audio_buffer = await loop.run_in_executor(
                    None, 
                    text_to_speech, 
                    result['translated_text'], 
                    target_language
                )
                audio_data = audio_buffer.read()
                encoded_audio = base64.b64encode(audio_data).decode("utf-8")
        except Exception as e:
            # TTS failed but translation succeeded, we can continue
            pass
        
        return JsonResponse({
            'translated_text': result['translated_text'],
            'source_language': result['src'],
            'target_language': result['dest'],
            'encoded_audio': encoded_audio
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                form.add_error(None, 'Invalid username or password')
    else:
        form = LoginForm()
    
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'signup.html', {'form': form})

def account(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Get the user's profile
    profile = request.user.profile
    
    context = {
        # User model fields
        'user': {
            'id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'date_joined': request.user.date_joined,
            'last_login': request.user.last_login,
        },
        # Profile model fields
        'profile': {
            'bio': profile.bio,
            'location': profile.location,
            'primary_language': profile.primary_language,
            'other_languages': profile.other_languages,
            'is_anonymous': profile.is_anonymous,
        },
        # Convenience fields
        'display_name': request.user.first_name or request.user.username,
    }
    
    return render(request, 'account.html', context)

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

