import asyncio
import base64
from django.shortcuts import render
from translator.services import translate_text
from tts.services import text_to_speech
from googletrans import LANGUAGES

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
        html_content += f'<option value="{lang_code}"{selected_attr}>{lang_name.title()}</option>'
    html_content += '</select>'
    return html_content

async def translate(request):
    lang = request.GET.get('target_language', DEFAULT_TARGET_LANGUAGE)
    text_to_translate = request.GET.get('text', DEFAULT_TEXT)

    # Translate the text using the specified target language.
    translated_text = translate_text(text_to_translate, lang)

    # Generate TTS audio
    loop = asyncio.get_running_loop()
    audio_buffer = await loop.run_in_executor(None, text_to_speech, translated_text, lang)
    audio_data = audio_buffer.read()
    encoded_audio = base64.b64encode(audio_data).decode("utf-8")

    context = {
        'text_to_translate': text_to_translate,
        'translated_text': translated_text,
        'encoded_audio': encoded_audio,
        'selected_language': lang,
        'language_dropdown': build_LANGUAGES_html(lang)
    }

    return render(request, 'translate.html', context)

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # Perform login logic here
        return HttpResponse("Login successful")
    return render(request, 'login.html')

def logout_view(request):
    # Perform logout logic here
    return HttpResponse("Logout successful")

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # Perform signup logic here
        return HttpResponse("Signup successful")
    return render(request, 'signup.html')

def account(request):
    # Perform account management logic here
    return HttpResponse("Account management page")

def about(request):
    # Render the about page
    return render(request, 'about.html')
