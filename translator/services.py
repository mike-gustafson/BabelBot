from googletrans import Translator, LANGUAGES
from functools import lru_cache
import asyncio

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
        return {}

async def translate_text(text, dest_lang='en', src_lang=None, max_retries=3):
    """
    Translate text to the target language.
    Includes retry logic and better error handling.
    """
    if not text:
        raise ValueError("Text cannot be empty")
        
    if not dest_lang:
        raise ValueError("Target language is required")
        
    for attempt in range(max_retries):
        try:
            translator = Translator()
            translator.timeout = 10
            
            # If source language is specified, use it
            if src_lang:
                result = await translator.translate(text, dest=dest_lang, src=src_lang)
            else:
                result = await translator.translate(text, dest=dest_lang)
                
            return {
                'original_text': text,
                'translated_text': result.text,
                'src': result.src,
                'dest': result.dest,
                'confidence': result.extra_data.get('confidence', 0)
            }
        except Exception as e:
            if attempt == max_retries - 1:
                raise Exception(f"Translation failed after {max_retries} attempts: {str(e)}")
            continue

def is_language_supported(language):
    """
    Check if a language is supported for translation
    """
    return language in get_available_languages()