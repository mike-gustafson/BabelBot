import asyncio
from asgiref.sync import sync_to_async
import base64
import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from translator.services import translate_text, get_available_languages
from tts.services import text_to_speech, is_language_supported, get_audio_base64
from googletrans import LANGUAGES
from .forms import TranslationForm, LoginForm, SignupForm, CustomUserCreationForm, ProfileForm
from django.contrib.auth import login, authenticate, logout, get_user
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Translation, Profile
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils import timezone
from ocr.services import detect_text
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .utils import get_or_create_profile, update_preferred_languages, get_preferred_languages

DEFAULT_TARGET_LANGUAGE = "es"
DEFAULT_TEXT = (
    "A long time ago, in a galaxy far, far away..."
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
                target_language=target_language
            )
        
        # Generate TTS if the language is supported
        encoded_audio = None
        try:
            if is_language_supported(target_language):
                encoded_audio = get_audio_base64(result['translated_text'], target_language)
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

@login_required
def account(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Get the user's profile
    profile = request.user.profile
    
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
        
        original_text = request.POST.get('original_text')
        target_lang = request.POST.get('target_lang')
        
        # Translate the new text
        result = await translate_text(original_text, target_lang)
        
        # Update the translation
        translation.original_text = original_text
        translation.translated_text = result['translated_text']
        translation.target_lang = target_lang
        
        # Wrap save operation in sync_to_async
        save_translation = sync_to_async(translation.save)
        await save_translation()
        
        return JsonResponse({
            'status': 'success',
            'translated_text': result['translated_text']
        })
    except Translation.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Translation not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
def delete_translation(request, translation_id):
    try:
        translation = Translation.objects.get(id=translation_id, user=request.user)
        translation.delete()
        return JsonResponse({'status': 'success'})
    except Translation.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Translation not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def about(request):
    return render(request, 'about.html')

@login_required
def home(request):
    """Home page view"""
    return render(request, 'home.html')

@login_required
def translate(request):
    """Translation view"""
    if request.method == 'POST':
        form = TranslationForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            target_language = form.cleaned_data['target_language']
            
            try:
                # Perform translation
                result = translate_text(text, target_language)
                
                if result.get('success'):
                    # Save translation
                    Translation.objects.create(
                        user=request.user,
                        original_text=text,
                        translated_text=result['translation'],
                        target_language=target_language
                    )
                    
                    messages.success(request, 'Translation successful!')
                    return render(request, 'translate.html', {
                        'form': form,
                        'translation': result['translation']
                    })
                else:
                    messages.error(request, result.get('error', 'Translation failed'))
            except Exception as e:
                messages.error(request, f'Error during translation: {str(e)}')
    else:
        form = TranslationForm()
    
    return render(request, 'translate.html', {
        'form': form,
        'languages': get_available_languages()
    })

@login_required
def history(request):
    """Translation history view"""
    translations = Translation.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'history.html', {'translations': translations})

@login_required
def settings(request):
    """User settings view"""
    if request.method == 'POST':
        languages = request.POST.getlist('preferred_languages')
        update_preferred_languages(request.user, languages)
        messages.success(request, 'Settings updated successfully!')
        return redirect('settings')
    
    profile = get_or_create_profile(request.user)
    return render(request, 'settings.html', {
        'profile': profile,
        'languages': get_available_languages()
    })

def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
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
        # Get the user
        user = form.user
        # Log the user in
        login(self.request, user)
        return super().form_valid(form)

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'password_reset_complete.html'

def index(request):
    languages = get_available_languages()
    return render(request, 'index.html', {'languages': languages})

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
        
        if not is_language_supported(language):
            return JsonResponse({'error': f'Language {language} is not supported'}, status=400)
        
        # Generate speech
        encoded_audio = get_audio_base64(text, language)
        
        return JsonResponse({
            'success': True,
            'encoded_audio': encoded_audio
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def account_delete_confirm(request):
    if request.method == 'POST':
        # Delete the user's profile first
        request.user.profile.delete()
        # Delete the user
        request.user.delete()
        # Logout the user
        logout(request)
        messages.success(request, 'Your account has been successfully deleted.')
        return redirect('home')
    
    return render(request, 'account_delete_confirm.html')

