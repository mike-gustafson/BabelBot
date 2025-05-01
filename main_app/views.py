import json
import logging
from asgiref.sync import sync_to_async
from django import forms
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout, get_user
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from googletrans import LANGUAGES
from ocr.services import detect_text
from tts.services import text_to_speech, is_language_supported, get_audio_base64
from translator.services import get_available_languages, translate_text
from googletrans import Translator
import asyncio

from .forms import TranslationForm, LoginForm, SignupForm, CustomUserCreationForm, ProfileForm
from .models import Translation, Profile
from .utils import get_or_create_profile, update_preferred_language, get_preferred_language

logger = logging.getLogger(__name__)

DEFAULT_TARGET_LANGUAGE = "es"
DEFAULT_TEXT = (
    "A long time ago, in a galaxy far, far away..."
)

# Create async versions of database operations
create_translation = sync_to_async(Translation.objects.create)
get_languages = sync_to_async(get_available_languages)
get_user_async = sync_to_async(get_user)
render_async = sync_to_async(render)
create_form = sync_to_async(TranslationForm)

def build_languages_html(selected_language, languages):
    """Build HTML for language select dropdown efficiently."""
    options = [
        f'<option value="{code}"{" selected" if code == selected_language else ""}>{name}</option>'
        for code, name in languages.items()
    ]
    return f'<select id="language-select" name="target_language"><option value="">Select a language</option>{"".join(options)}</select>'

async def translate_view(request):
    try:
        # Wrap session access in sync_to_async
        text_to_translate = await sync_to_async(lambda: request.session.get('text_to_translate', DEFAULT_TEXT))()
        lang = await sync_to_async(lambda: request.session.get('target_language', DEFAULT_TARGET_LANGUAGE))()
        
        # Get languages directly from the translator service
        languages = await get_languages()
        
        # Create form instance with languages
        form = await sync_to_async(TranslationForm)(languages=languages, selected_language=lang)
        
        return await sync_to_async(render)(request, 'translate.html', {
            'form': form,
            'text_to_translate': text_to_translate,
            'translated_text': "",
            'languages': languages
        })
        
    except Exception as e:
        logger.error(f"Error in translate_view: {str(e)}")
        # Create form instance with fallback languages
        form = await sync_to_async(TranslationForm)(languages=LANGUAGES, selected_language=DEFAULT_TARGET_LANGUAGE)
        
        return await sync_to_async(render)(request, 'translate.html', {
            'form': form,
            'text_to_translate': DEFAULT_TEXT,
            'translated_text': "An error occurred. Please try again.",
            'languages': LANGUAGES
        })

@login_required
def translate(request):
    """Handle both GET and POST requests for translation"""
    if request.method == 'GET':
        # Get available languages
        languages = get_available_languages()
        
        # Create form with languages
        form = TranslationForm(languages=languages)
        
        return render(request, 'translate.html', {
            'form': form,
            'languages': languages
        })
    
    elif request.method == 'POST':
        # Get form data
        text = request.POST.get('text_to_translate')
        target_lang = request.POST.get('target_language')
        
        # Print to terminal
        print(f"Text to translate: {text}")
        print(f"Target language: {target_lang}")
        
        # Perform translation in a separate thread
        translator = Translator()
        result = asyncio.run(translator.translate(text, dest=target_lang))
        
        # Print translation result to terminal
        print(f"Translated text: {result.text}")
        print(f"Source language: {result.src}")
        print(f"Target language: {result.dest}")
        
        # Return to the same page with translation
        return render(request, 'translate.html', {
            'form': TranslationForm(languages=get_available_languages()),
            'languages': get_available_languages(),
            'translation': result.text,
            'source_language': result.src,
            'target_language': result.dest
        })

@login_required
@require_http_methods(["POST"])
async def perform_translation(request):
    """Handle POST requests - perform the translation"""
    try:
        # Get data from request
        data = json.loads(request.body)
        text = data.get('text_to_translate')
        target_lang = data.get('target_language')
        
        # Validate input
        if not text or not target_lang:
            return JsonResponse({
                'error': 'Text and target language are required'
            }, status=400)
        
        # Get translation - use sync_to_async since translate_text is synchronous
        result = await sync_to_async(translate_text)(text, target_lang)
        
        # Save translation if user is authenticated - use sync_to_async
        if request.user.is_authenticated:
            await create_translation(
                user=request.user,
                original_text=text,
                translated_text=result['translated_text'],
                target_language=target_lang,
                translation_type='typed'
            )
        
        # Return translation result
        return JsonResponse({
            'success': True,
            'translation': result['translated_text'],
            'source_language': result['src'],
            'target_language': result['dest']
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

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

@login_required
def account(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Get or create the user's profile
    profile = get_or_create_profile(request.user)
    
    # Get the user's translations, ordered by most recent first
    translations = request.user.translation_set.all().order_by('-created_at')
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('account')
    else:
        form = ProfileForm(instance=profile, user=request.user)
    
    # Get available languages for the edit form
    languages = LANGUAGES.items()
    
    context = {
        'user': request.user,
        'profile': profile,
        'translations': translations,
        'form': form,
        'display_name': request.user.first_name or request.user.username,
        'languages': languages,
    }
    
    return render(request, 'account.html', context)

@login_required
@require_http_methods(["POST"])
async def edit_translation(request):
    try:
        translation_id = request.POST.get('translation_id')
        # Wrap database operations in sync_to_async
        get_translation = sync_to_async(lambda: Translation.objects.get(id=translation_id, user=request.user))
        translation = await get_translation()
        
        # Update translation
        translation.original_text = request.POST.get('original_text', translation.original_text)
        translation.translated_text = request.POST.get('translated_text', translation.translated_text)
        translation.target_language = request.POST.get('target_language', translation.target_language)
        
        # Save the updated translation
        save_translation = sync_to_async(lambda: translation.save())
        await save_translation()
        
        return JsonResponse({
            'success': True,
            'message': 'Translation updated successfully'
        })
    except Translation.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Translation not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
@require_http_methods(["POST"])
def delete_translation(request, translation_id):
    try:
        translation = Translation.objects.get(id=translation_id, user=request.user)
        translation.delete()
        return JsonResponse({
            'success': True,
            'message': 'Translation deleted successfully'
        })
    except Translation.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Translation not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

def about(request):
    return render(request, 'about.html')

@login_required
def home(request):
    return render(request, 'home.html')

@login_required
def history(request):
    translations = Translation.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'history.html', {'translations': translations})

@login_required
def settings(request):
    profile = get_or_create_profile(request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('settings')
    else:
        form = ProfileForm(instance=profile, user=request.user)
    
    return render(request, 'settings.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'register.html', {'form': form})

class CustomPasswordResetView(PasswordResetView):
    template_name = 'password_reset.html'
    email_template_name = 'registration/password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')
    
    def form_valid(self, form):
        # Save the new password
        form.save()
        return super().form_valid(form)

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'password_reset_complete.html'

def index(request):
    return render(request, 'index.html')

@csrf_exempt
@require_http_methods(["POST"])
def ocr(request):
    try:
        image_data = request.FILES['image'].read()
        text = detect_text(image_data)
        return JsonResponse({
            'success': True,
            'text': text
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def tts(request):
    try:
        text = request.POST.get('text')
        language = request.POST.get('language', 'en')
        
        if not text:
            return JsonResponse({
                'success': False,
                'error': 'Text is required'
            }, status=400)
            
        if not is_language_supported(language):
            return JsonResponse({
                'success': False,
                'error': f'Language {language} is not supported'
            }, status=400)
            
        audio_base64 = get_audio_base64(text, language)
        
        return JsonResponse({
            'success': True,
            'audio': audio_base64
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
def account_delete_confirm(request):
    return render(request, 'account_delete_confirm.html')

