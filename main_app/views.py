# Standard library imports
import json
import logging

# Third-party imports
from asgiref.sync import sync_to_async
import requests

# Django imports
from django.contrib import messages
from django.contrib.auth import (
    login, authenticate, logout, get_user
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import (
    PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView
)
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.csrf import csrf_exempt

# Local application imports
from translator.services import get_available_languages, translate_text
from .forms import (
    TranslateFromTextForm, TranslateFromOCRForm,
    LoginForm, CustomUserCreationForm, ProfileForm
)
from .models import Translation, Profile
from .utils import get_or_create_profile

logger = logging.getLogger(__name__)

DEFAULT_TARGET_LANGUAGE = "es"
DEFAULT_TEXT = ("A long time ago, in a galaxy far, far away...")

# Create async versions of database operations
create_translation = sync_to_async(Translation.objects.create)
get_languages = sync_to_async(get_available_languages)
get_user_async = sync_to_async(get_user)
render_async = sync_to_async(render)
create_form = sync_to_async(TranslateFromTextForm)
get_translation = sync_to_async(lambda id, user: Translation.objects.get(id=id, user=user))
save_model = sync_to_async(lambda model: model.save())
is_authenticated = sync_to_async(lambda user: user.is_authenticated)
get_profile = sync_to_async(get_or_create_profile)
get_all_translations = sync_to_async(lambda: list(Translation.objects.all()))
get_user_translations = sync_to_async(lambda user: list(Translation.objects.filter(user=user).order_by('-created_at')))
get_null_user_translations = sync_to_async(lambda: list(Translation.objects.filter(user__isnull=True)))
get_user_by_username = sync_to_async(lambda username: User.objects.get(username=username))
get_translation_count = sync_to_async(lambda: Translation.objects.count())
get_user_translation_count = sync_to_async(lambda user: Translation.objects.filter(user=user).count())
get_null_user_translation_count = sync_to_async(lambda: Translation.objects.filter(user__isnull=True).count())
get_user_id = sync_to_async(lambda translation: translation.user.id if translation.user else None)
format_languages = sync_to_async(lambda: [(code, name) for code, name in get_available_languages().items()])
save_form = sync_to_async(lambda form: form.save())

@require_http_methods(["GET", "POST"])
@csrf_exempt
def home(request):
    try:
        login_form = LoginForm()
        signup_form = CustomUserCreationForm()
        show_signup = False

        if request.method == 'POST':
            """
            function: Handle home page requests and login/signup form submissions
            parameters: request - the request object
            returns: render the home page template with appropriate forms
            """
            if 'login-submit' in request.POST:
                """
                function: Handle login form submissions
                parameters: request - the request object
                returns: redirect to the home page or error message
                """
                login_form = LoginForm(request.POST)
                if login_form.is_valid():
                    username = login_form.cleaned_data.get('username')
                    password = login_form.cleaned_data.get('password')
                    user = authenticate(request, username=username, password=password)
                    if user is not None:
                        login(request, user)
                        messages.success(request, 'You have been successfully logged in.')
                        return redirect('home')
                    else:
                        logger.info(f"Failed login attempt for username: {username}")
                        login_form.add_error(None, 'Invalid username or password')
                        messages.error(request, 'Invalid username or password.')
                else:
                    logger.info("Invalid login form submission")
                    messages.error(request, 'Please correct the errors below.')
            
            elif 'signup-submit' in request.POST:
                """
                function: Handle signup form submissions
                parameters: request - the request object
                returns: redirect to the home page or error message
                """
                signup_form = CustomUserCreationForm(request.POST)
                show_signup = True
                if signup_form.is_valid():
                    user = signup_form.save()
                    login(request, user)
                    messages.success(request, 'Account created successfully!')
                    return redirect('home')
                else:                                    
                    form_data = signup_form.data.copy()
                    signup_form = CustomUserCreationForm(data=form_data)
                    signup_form.is_valid()
        else:
            """
            function: Serve the home page template
            parameters: request - the request object
            returns: render the home page template with appropriate forms
            """
            context = {
                'login_form': login_form,
                'signup_form': signup_form,
                'show_signup': show_signup
            }
        
            return render(request, 'home.html', context)
    except Exception as e:
        logger.error(f"Error in home view: {str(e)}")
        messages.error(request, 'An error occurred. Please try again.')
        return render(request, 'home.html', {
            'login_form': LoginForm(),
            'signup_form': CustomUserCreationForm(),
            'show_signup': False
        })

@require_http_methods(["GET"])
@csrf_exempt
def about(request):
    """
    function: Serve the about page template
    parameters: request - the request object
    returns: render the about page template
    """
    try:
        return render(request, 'about.html')
    except Exception as e:
        logger.error(f"Error in about view: {str(e)}")
        messages.error(request, 'An error occurred. Please try again.')
        return render(request, 'home.html')
    
@require_http_methods(["GET","POST"])
@csrf_exempt
async def translate(request):
    if request.method == 'POST':
        """
        function: Handle translation requests from the frontend
        parameters: request - the request object
        returns: JsonResponse with the translation result or an error message
        """
        try:
            # Check authentication status using sync_to_async
            is_authenticated = await sync_to_async(lambda: request.user.is_authenticated)()

            # Get data from JSON request body
            data = json.loads(request.body)
            text = data.get('text')
            target_language = data.get('target_language')

            if not text or not target_language:
                return JsonResponse({
                    'error': 'Text and target language are required'
                }, status=400)

            # Make request to translator app using sync_to_async
            response = await sync_to_async(lambda: requests.post(
                request.build_absolute_uri('/translator/translate/'),
                json={
                    'text': text,
                    'target_language': target_language
                },
                headers={
                    'Content-Type': 'application/json',
                    'X-CSRFToken': request.COOKIES.get('csrftoken', '')
                }
            ))()

            if response.status_code != 200:
                return JsonResponse({
                    'error': 'Translation service error'
                }, status=500)
            response_data = response.json()

            # Save translation if user is authenticated - use sync_to_async
            if is_authenticated:
                try:
                    await create_translation(
                        user=request.user,
                        original_text=text,
                        translated_text=response_data['translation'],
                        target_language=target_language,
                        translation_type='typed'
                    )
                except Exception as e:
                    logger.error(f"Error saving translation in translate view: {str(e)}")
                    raise
                
            # Return the translation response
            return JsonResponse(response_data)

        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)
            
    else:
        """
        function: Serve the translation page template
        parameters: request - the request object
        returns: render the translation page template
        """
        # Get available languages using the pre-defined get_languages function
        languages = await get_languages()
    
        # Create both forms with languages using sync_to_async
        text_form = await sync_to_async(TranslateFromTextForm)(languages=languages)
        ocr_form = await sync_to_async(TranslateFromOCRForm)(languages=languages)
    
        # Use sync_to_async for render
        return await sync_to_async(render)(request, 'translate.html', {
            'text_form': text_form,
            'ocr_form': ocr_form,
            'languages': languages,
        })

@require_http_methods(["GET"])
@csrf_exempt
def logout_view(request):
    """
    function: Handle user logout
    parameters: request - the request object
    returns: redirect to the home page
    """
    try:
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
    except Exception as e:
        logger.error(f"Error during logout: {str(e)}")
        messages.error(request, 'An error occurred during logout.')
    return redirect('home')

@require_http_methods(["GET", "POST"])
@csrf_exempt
def signup(request):
    if request.method == 'POST':
        """
        function: Handle signup form submissions
        parameters: request - the request object
        returns: redirect to the home page or error message
        """
        form = CustomUserCreationForm(request.POST)
        
        if form.is_valid():
            print("Form is valid")
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            
            # Check if username exists
            if User.objects.filter(username=username).exists():
                form.add_error('username', 'Username taken')
                return render(request, 'home.html', {
                    'signup_form': form,
                    'login_form': LoginForm(),
                    'show_signup': True
                })
            
            # Check if email exists
            if User.objects.filter(email=email).exists():
                form.add_error('email', 'An account using that email has already been created')
                return render(request, 'home.html', {
                    'signup_form': form,
                    'login_form': LoginForm(),
                    'show_signup': True
                })
            
            # If both checks pass, create the user
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('home')
        else:
            print("\nForm validation failed!")
            print(f"Form errors: {form.errors}")
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"Field '{field}' error: {error}")
            
            # If form is invalid, show the form with errors
            return render(request, 'home.html', {
                'signup_form': form,
                'login_form': LoginForm(),
                'show_signup': True
            })
    return redirect('account')

@login_required
@require_http_methods(["GET", "POST"])
async def account(request):
    """
    function: Serve the account page template
    parameters: request - the request object
    returns: render the account page template
    """
    profile = await get_profile(request.user)
    translations = await get_user_translations(request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile, user=request.user)
        if form.is_valid():
            await save_form(form)
            messages.success(request, 'Profile updated successfully!')
            return redirect('account')
    else:
        form = ProfileForm(instance=profile, user=request.user)
    
    languages = await format_languages()

    context = {
        'user': request.user,
        'profile': profile,
        'translations': translations,
        'form': form,
        'display_name': request.user.first_name or request.user.username,
        'languages': languages,
    }
    
    return await render_async(request, 'account.html', context)

@login_required
@require_http_methods(["POST"])
async def handle_translation(request, translation_id=None):
    """
    function: Handle translation edit and delete operations
    parameters: 
        request - the request object
        translation_id - the ID of the translation to edit/delete (for delete operations)
    returns: JsonResponse with success or error message
    """
    try:
        """
        function: DELETE the translation
        parameters:
            request - the request object
            translation_id - the ID of the translation to delete
        returns: if Params has translation_id, delete the translation and return JsonResponse with success or error message.
        """
        if translation_id is not None:
            translation = await get_translation(translation_id, request.user)
            await sync_to_async(translation.delete)()
            return JsonResponse({
                'success': True,
                'message': 'Translation deleted successfully'
            })
        
        """
        function: EDIT the translation
        parameters:
            request - the request object
        returns: If Params does NOT have a translation_id, edit the translation and return JsonResponse with success or error message.
        """
        translation_id = request.POST.get('translation_id')
        translation = await get_translation(translation_id, request.user)
        
        new_original_text = request.POST.get('original_text', translation.original_text)
        new_target_language = request.POST.get('target_language', translation.target_language)
        
        needs_retranslation = (
            new_original_text != translation.original_text or 
            new_target_language != translation.target_language
        )
        
        translation.original_text = new_original_text
        translation.target_language = new_target_language
        
        if needs_retranslation:
            result = await translate_text(
                translation.original_text,
                translation.target_language
            )
            translation.translated_text = result['translated_text']
        else:
            translation.translated_text = request.POST.get('translated_text', translation.translated_text)
        
        await save_model(translation)
        
        return JsonResponse({
            'success': True,
            'message': 'Translation updated successfully',
            'translated_text': translation.translated_text
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
@require_http_methods(["GET", "POST"])
def account_delete_confirm(request):
    if request.method == 'POST':
        """
        function: Handle account delete confirmation form submissions
        parameters: request - the request object
        returns: redirect to the home page or error message
        """
        try:
            user = request.user
            user.delete()
            logout(request)
            messages.success(request, 'Your account has been deleted successfully.')
            return redirect('home')
        except Exception as e:
            logger.error(f"Error in account_delete_confirm view: {str(e)}")
            messages.error(request, 'An error occurred. Please try again.')
            return redirect('account_delete_confirm')
        
    """
    function: Serve the account delete confirmation page template
    parameters: request - the request object
    returns: render the account delete confirmation page template
    """
    try: 
        return render(request, 'account_delete_confirm.html')
    except Exception as e:
        logger.error(f"Error in account_delete_confirm view: {str(e)}")
        messages.error(request, 'An error occurred. Please try again.')
        return render(request, 'home.html')

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
        form.save()
        return super().form_valid(form)

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'password_reset_complete.html'
