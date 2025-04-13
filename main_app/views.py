import asyncio
import base64
from django.http import HttpResponse
from translator.services import translate_text
from tts.services import text_to_speech
from googletrans import LANGUAGES

# Default language if not overridden by a query parameter
DEFAULT_TARGET_LANGUAGE = "es"

test_text_long = (
    "A long time ago, in a galaxy far, far away. It is a period of civil war. Rebel "
    "spaceships, striking from a hidden base, have won their first victory against the evil "
    "Galactic Empire. During the battle, Rebel spies managed to steal secret plans to the Empire's "
    "ultimate weapon, the DEATH STAR, an armored space station with enough power to destroy an entire "
    "planet. Pursued by the Empire's sinister agents, Princess Leia races home aboard her starship, "
    "custodian of the stolen plans that can save her people and restore freedom to the galaxy..."
)

def build_LANGUAGES_html(selected_language):
    html_content = '<h3>Available Languages</h3><select id="language-select">'
    html_content += '<option value="">Select a language</option>'
    for lang_code, lang_name in LANGUAGES.items():
        selected_attr = ' selected' if lang_code == selected_language else ''
        html_content += f'<option value="{lang_code}"{selected_attr}>{lang_name.title()}</option>'
    html_content += '</select>'
    return html_content

async def home(request):
    # Read target_language from query parameters; use default if not provided.
    lang = request.GET.get('target_language', DEFAULT_TARGET_LANGUAGE)
    
    # Translate text using the specified target language.
    translated_text = translate_text(test_text_long, lang)
    
    # Convert the translated text to speech using an executor.
    loop = asyncio.get_running_loop()
    audio_buffer = await loop.run_in_executor(None, text_to_speech, translated_text, lang)
    
    # Encode the audio data to base64 for embedding in HTML.
    audio_data = audio_buffer.read()
    encoded_audio = base64.b64encode(audio_data).decode("utf-8")

    # Build the dropdown HTML, pre-selecting the current language.
    languages_html = build_LANGUAGES_html(lang)
    
    # Create the HTML response including the audio player and a simple JavaScript snippet
    # to update the selected language dynamically.
    html_content = (
        f'<h1>Welcome to BabelBot 1.0</h1>'
        f'{languages_html}'
        f'<h2>{translated_text}</h2>'
        f'<audio controls>'
        f'  <source src="data:audio/mp3;base64,{encoded_audio}" type="audio/mp3">'
        f'  Your browser does not support the audio element.'
        f'</audio>'
        f'<script>'
        f'  document.getElementById("language-select").addEventListener("change", function() {{'
        f'    var selectedLang = this.value;'
        f'    window.location.href = window.location.pathname + "?target_language=" + selectedLang;'
        f'  }});'
        f'</script>'
    )
    return HttpResponse(html_content)
