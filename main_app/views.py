import asyncio
import base64
from django.http import HttpResponse
from translator.services import translate_text
from tts.services import text_to_speech

test_text_en = "Hello world!"
test_text_es = "¡Hola mundo!"
test_text_fr = "Bonjour le monde!"
test_text_de = "Hallo Welt!"
test_text_it = "Ciao mondo!"
test_text_long = "A long time ago, in a galaxy far, far away. It is a period of civil war. Rebel spaceships, striking from a hidden base, have won their first victory against the evil Galactic Empire. During the battle, Rebel spies managed to steal secret plans to the Empire's ultimate weapon, the DEATH STAR, an armored space station with enough power to destroy an entire planet. Pursued by the Empire's sinister agents, Princess Leia races home aboard her starship, custodian of the stolen plans that can save her people and restore freedom to the galaxy..."

target_language = "ru"

async def home(request):
    # Translate text to English
    translated_text = translate_text(test_text_long, target_language)
    
    # Convert the translated text to speech
    loop = asyncio.get_running_loop()
    audio_buffer = await loop.run_in_executor(None, text_to_speech, translated_text, target_language)
    
    # Encode the audio data to base64 for embedding in HTML
    audio_data = audio_buffer.read()
    encoded_audio = base64.b64encode(audio_data).decode("utf-8")

    # Create the HTML response with the audio player    
    html_content = (
        f'<h1>Welcome to BableBot 1.0</h1>'
        f'<h2>{translated_text}</h2>'
        f'<audio controls>'
        f'  <source src="data:audio/mp3;base64,{encoded_audio}" type="audio/mp3">'
        f'  Your browser does not support the audio element.'
        f'</audio>'
    )
    return HttpResponse(html_content)
