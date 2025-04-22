import io
from gtts import gTTS

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
