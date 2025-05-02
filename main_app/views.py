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

from .forms import TranslateFromTextForm, TranslateFromOCRForm, LoginForm, SignupForm, CustomUserCreationForm, ProfileForm
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
create_form = sync_to_async(TranslateFromTextForm)

def build_languages_html(selected_language, languages):
    """Build HTML for language select dropdown efficiently."""
    options = [
        f'<option value="{code}"{" selected" if code == selected_language else ""}>{name}</option>'
        for code, name in languages.items()
    ]
    return f'<select id="language-select" name="target_language"><option value="">Select a language</option>{"".join(options)}</select>'

def translate(request):
    """Handle both GET and POST requests for translation"""
    if request.method == 'GET':
        # Get available languages
        languages = get_available_languages()
        
        # Create both forms with languages
        text_form = TranslateFromTextForm(languages=languages)
        ocr_form = TranslateFromOCRForm(languages=languages)
        
        return render(request, 'translate.html', {
            'text_form': text_form,
            'ocr_form': ocr_form,
            'languages': languages,
        })
    
    elif request.method == 'POST':
        # Check if it's an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Get data from either JSON or form data
            if request.content_type == 'application/json':
                try:
                    data = json.loads(request.body)
                    text = data.get('text')
                    target_lang = data.get('target_language')
                    form_type = data.get('form_type', 'text')
                except json.JSONDecodeError:
                    return JsonResponse({
                        'error': 'Invalid JSON data'
                    }, status=400)
            else:
                text = request.POST.get('text')
                target_lang = request.POST.get('target_language')
                form_type = request.POST.get('form_type', 'text')
            
            if not text or not target_lang:
                return JsonResponse({
                    'error': 'Please provide both text and target language'
                }, status=400)
            
            try:
                # Perform translation using the translation service
                result = asyncio.run(translate_text(text, target_lang))
                
                # Create and save translation record only if user is authenticated
                if request.user.is_authenticated:
                    logger.info(f"translate view - Saving translation for user {request.user.username}")
                    logger.info(f"Original text: {text[:50]}...")
                    logger.info(f"Target language: {target_lang}")
                    try:
                        translation = Translation.objects.create(
                            user=request.user,
                            original_text=text,
                            translated_text=result['translated_text'],
                            target_language=target_lang,
                            translation_type='typed'  # Always set translation_type to 'typed'
                        )
                        logger.info(f"Translation saved successfully with ID: {translation.id}")
                    except Exception as e:
                        logger.error(f"Error saving translation in translate view: {str(e)}")
                        raise
                
                return JsonResponse({
                    'success': True,
                    'translated_text': result['translated_text'],
                    'source_language': result['src'],
                    'target_language': result['dest']
                })
            except Exception as e:
                logger.error(f"Error in translate view: {str(e)}")
                return JsonResponse({
                    'error': f'Translation error: {str(e)}'
                }, status=500)
        else:
            # Handle non-AJAX requests (fallback)
            messages.error(request, 'Please enable JavaScript for this feature')
            return redirect('translate')

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
            logger.info(f"perform_translation view - Saving translation for user {request.user.username}")
            logger.info(f"Original text: {text[:50]}...")
            logger.info(f"Target language: {target_lang}")
            try:
                translation = await create_translation(
                    user=request.user,
                    original_text=text,
                    translated_text=result['translated_text'],
                    target_language=target_lang,
                    translation_type='typed'
                )
                logger.info(f"Translation saved successfully with ID: {translation.id}")
            except Exception as e:
                logger.error(f"Error saving translation in perform_translation view: {str(e)}")
                raise
        
        # Return translation result
        return JsonResponse({
            'success': True,
            'translation': result['translated_text'],
            'source_language': result['src'],
            'target_language': result['dest']
        })
        
    except json.JSONDecodeError:
        logger.error("Invalid JSON in perform_translation view")
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error in perform_translation view: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

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
    
    # Debug: Print all translations in the database
    all_translations = Translation.objects.all()
    logger.info(f"Total translations in database: {all_translations.count()}")
    for t in all_translations:
        logger.info(f"DB Translation - ID: {t.id}, User: {t.user.username if t.user else 'None'}, Created: {t.created_at}")
    
    # Get the user's translations using a more explicit query
    translations = Translation.objects.filter(user=request.user).order_by('-created_at')
    
    # Debug logging with dates
    logger.info(f"Account view - User: {request.user.username} (ID: {request.user.id})")
    logger.info(f"Number of translations found for user: {translations.count()}")
    
    # Also check for any translations with null users
    null_user_translations = Translation.objects.filter(user__isnull=True)
    logger.info(f"Number of translations with null users: {null_user_translations.count()}")
    
    for translation in translations:
        logger.info(f"User Translation ID: {translation.id}")
        logger.info(f"Created at: {translation.created_at}")
        logger.info(f"Original: {translation.original_text[:50]}")
        logger.info(f"Target Language: {translation.target_language}")
        logger.info(f"User ID: {translation.user.id}")
        logger.info("---")
    
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

def home(request):
    if request.method == 'POST':
        # Handle login form submission
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
    
    return render(request, 'home.html', {'form': form})

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
        
        # Log the translation attempt
        logger.info(f"Translation attempt - User authenticated: {request.user.is_authenticated}")
        
        # Save translation if user is authenticated - use sync_to_async
        if request.user.is_authenticated:
            try:
                translation = await create_translation(
                    user=request.user,
                    original_text=text,
                    translated_text=result['translated_text'],
                    target_language=target_language,
                    translation_type='typed'  # Always set translation_type to 'typed'
                )
                logger.info(f"Translation saved successfully - ID: {translation.id}")
            except Exception as e:
                logger.error(f"Error saving translation: {str(e)}")
        
        # Return translation result
        return JsonResponse({
            'success': True,
            'translated_text': result['translated_text'],
            'source_language': result['src'],
            'target_language': result['dest']
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

