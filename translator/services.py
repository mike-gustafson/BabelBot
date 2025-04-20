from googletrans import Translator, LANGUAGES
from asgiref.sync import sync_to_async
import asyncio

def get_available_languages():
    """
    Get a list of available languages from Google Translate.
    Returns a dictionary of language codes and their names.
    """
    formatted_languages = {code: name for code, name in LANGUAGES.items()}
    return formatted_languages

async def translate_text(text, dest_lang='en', max_retries=3):
    """
    Asynchronously translate text to the target language.
    """
    translator = Translator()
    translator.timeout = 10
    
    for attempt in range(max_retries):
        try:
            # googletrans.Translator.translate is already async, so we can await it directly
            result = await translator.translate(text, dest=dest_lang)
            
            return {
                'source_text': text,
                'translated_text': result.text,
                'src': result.src,
                'dest': result.dest,
                'confidence': result.extra_data.get('confidence', 0)
            }
            
        except Exception as e:
            if attempt < max_retries - 1:
                await asyncio.sleep(1)
                continue
            return {
                'source_text': text,
                'translated_text': f'Translation error: {str(e)}',
                'src': 'unknown',
                'dest': dest_lang,
                'confidence': 0
            }