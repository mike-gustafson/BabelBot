import io
import base64
from gtts import gTTS
from gtts.lang import tts_langs

def get_supported_languages():
    """Get a list of supported languages for TTS."""
    return tts_langs()

def is_language_supported(language):
    """Check if a language is supported for TTS."""
    return language in get_supported_languages()

def text_to_speech(text, language='en'):
    """Convert text to speech using Google Text-to-Speech."""
    try:
        # Create gTTS object
        tts = gTTS(text=text, lang=language)
        
        # Create a bytes buffer
        audio_buffer = io.BytesIO()
        
        # Save the audio to the buffer
        tts.write_to_fp(audio_buffer)
        
        # Reset buffer position
        audio_buffer.seek(0)
        
        return audio_buffer
    except Exception as e:
        raise Exception(f"Error generating speech: {str(e)}")

def get_audio_base64(text, language='en'):
    """Convert text to speech and return as base64 encoded string."""
    try:
        audio_buffer = text_to_speech(text, language)
        audio_data = audio_buffer.read()
        return base64.b64encode(audio_data).decode("utf-8")
    except Exception as e:
        raise Exception(f"Error encoding audio: {str(e)}")
