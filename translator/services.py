from googletrans import Translator, LANGUAGES
from asgiref.sync import sync_to_async
import asyncio
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)

@lru_cache(maxsize=1000)
def get_available_languages():
    """
    Get a list of available languages from Google Translate.
    Returns a dictionary of language codes and their names.
    Cached to improve performance.
    """
    try:
        formatted_languages = {code: name for code, name in LANGUAGES.items()}
        return formatted_languages
    except Exception as e:
        logger.error(f"Error getting available languages: {str(e)}")
        return {}

def _translate_sync(text, dest_lang='en', src_lang=None):
    """
    Synchronous translation function with improved error handling
    """
    try:
        translator = Translator()
        translator.timeout = 10
        
        # If source language is specified, use it
        if src_lang:
            result = translator.translate(text, dest=dest_lang, src=src_lang)
        else:
            result = translator.translate(text, dest=dest_lang)
            
        return {
            'source_text': text,
            'translated_text': result.text,
            'src': result.src,
            'dest': result.dest,
            'confidence': result.extra_data.get('confidence', 0)
        }
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        raise

async def translate_text(text, dest_lang='en', src_lang=None, max_retries=3):
    """
    Asynchronously translate text to the target language.
    Includes retry logic and better error handling.
    """
    if not text:
        raise ValueError("Text cannot be empty")
        
    if not dest_lang:
        raise ValueError("Target language is required")
        
    for attempt in range(max_retries):
        try:
            # Run the synchronous translation in a thread pool
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(None, _translate_sync, text, dest_lang, src_lang)
            return result
            
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"Translation attempt {attempt + 1} failed: {str(e)}")
                await asyncio.sleep(1)
                continue
            logger.error(f"Translation failed after {max_retries} attempts: {str(e)}")
            return {
                'source_text': text,
                'translated_text': f'Translation error: {str(e)}',
                'src': src_lang or 'unknown',
                'dest': dest_lang,
                'confidence': 0
            }

def is_language_supported(language):
    """
    Check if a language is supported for translation
    """
    return language in get_available_languages()