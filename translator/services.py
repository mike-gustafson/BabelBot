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

def _translate_sync(text, dest_lang='en'):
    """
    Synchronous translation function
    """
    translator = Translator()
    translator.timeout = 10
    result = translator.translate(text, dest=dest_lang)
    return {
        'source_text': text,
        'translated_text': result.text,
        'src': result.src,
        'dest': result.dest,
        'confidence': result.extra_data.get('confidence', 0)
    }

async def translate_text(text, dest_lang='en', max_retries=3):
    """
    Asynchronously translate text to the target language.
    """
    for attempt in range(max_retries):
        try:
            # Run the synchronous translation in a thread pool
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(None, _translate_sync, text, dest_lang)
            return result
            
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