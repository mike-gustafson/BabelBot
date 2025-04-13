import asyncio
import base64
from django.http import HttpResponse
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

async def home(request):
    
    lang = request.GET.get('target_language', DEFAULT_TARGET_LANGUAGE)
    text_to_translate = request.GET.get('text', DEFAULT_TEXT)
    
    # Translate the text using the specified target language.
    translated_text = translate_text(text_to_translate, lang)
    
    # Generate TTS audio (offloading the synchronous TTS function to a worker thread)
    loop = asyncio.get_running_loop()
    audio_buffer = await loop.run_in_executor(None, text_to_speech, translated_text, lang)
    audio_data = audio_buffer.read()
    encoded_audio = base64.b64encode(audio_data).decode("utf-8")
        
    # Build HTML.
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>BabelBot 1.0</title>
        <style>
            body {{
                font-family: sans-serif;
                margin: 20px;
            }}
            .container {{
                display: flex;
                align-items: flex-start;
                gap: 20px;
            }}
            .column {{
                flex: 1;
            }}
            .center-column {{
                width: 150px;
                text-align: center;
            }}
            textarea {{
                width: 100%;
                height: 300px;
            }}
            #translated_text {{
                border: 1px solid #ccc;
                padding: 10px;
                min-height: 300px;
            }}
            /* Optional: styling for the language dropdown and button */
            #language-select {{
                width: 100%;
                margin-bottom: 10px;
            }}
            button {{
                width: 100%;
                padding: 10px;
                font-size: 1em;
            }}
        </style>
    </head>
    <body>
        <h1>Welcome to BabelBot 1.0</h1>
        <form method="get" id="translate-form">
            <div class="container">
                <div class="column">
                    <h3>Input Text</h3>
                    <textarea name="text" id="original_text">{text_to_translate}</textarea>
                </div>
                <div class="center-column">
                    {build_LANGUAGES_html(lang)}
                    <br/>
                    <button type="submit">Translate</button>
                </div>
                <div class="column">
                    <h3>Translated Text</h3>
                    <div id="translated_text">{translated_text}</div>
                    <br/>
                    <div id="audio_container">
                        <audio controls>
                            <source src="data:audio/mp3;base64,{encoded_audio}" type="audio/mp3">
                            Your browser does not support the audio element.
                        </audio>
                    </div>
                </div>
            </div>
        </form>
    </body>
    </html>
    """
    
    return HttpResponse(html_content)
