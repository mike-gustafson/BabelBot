import io
from gtts import gTTS
from gtts.lang import tts_langs

def text_to_speech(text, lang='en'):
    """
    Convert the provided text to speech using gTTS and return the audio as a BytesIO buffer.
    
    Args:
        text (str): The text to convert.
        lang (str): The language code (default 'en').
    
    Returns:
        BytesIO: An in-memory buffer containing the MP3 audio data.
    """
    supported_langs = tts_langs()
    if lang not in supported_langs:   
        text = "The Selected Language does not support audio translation."
        lang = 'en'
    else:
        text = text
        lang = lang
        
    tts = gTTS(text=text, lang=lang)
    audio_buffer = io.BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)
    return audio_buffer
