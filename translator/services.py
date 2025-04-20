from googletrans import Translator
import asyncio
from requests.exceptions import RequestException

def get_available_languages():
    """
    Get a list of available languages from Google Translate.
    Returns a dictionary of language codes and their names.
    """
    try:
        translator = Translator()
        languages = translator.get_languages()
        # Format the languages in a user-friendly way
        formatted_languages = {code: f"{name} ({code})" for code, name in languages.items()}
        return formatted_languages
    except Exception as e:
        # Return a basic set of languages if the translator fails
        fallback_languages = {
            'en': 'English (en)',
            'es': 'Spanish (es)',
            'fr': 'French (fr)',
            'de': 'German (de)',
            'it': 'Italian (it)',
            'pt': 'Portuguese (pt)',
            'ru': 'Russian (ru)',
            'zh-cn': 'Chinese Simplified (zh-cn)',
            'ja': 'Japanese (ja)',
            'ko': 'Korean (ko)'
        }
        return fallback_languages

async def translate_text(text, dest_lang='en', max_retries=3):
    for attempt in range(max_retries):
        try:
            translator = Translator()
            
            # Set a longer timeout for Heroku
            translator.timeout = 10
            
            # Translate the text
            result = translator.translate(text, dest=dest_lang)
            
            return {
                'translated_text': result.text,
                'src': result.src,
                'dest': result.dest,
                'confidence': result.extra_data.get('confidence', 0)
            }
            
        except RequestException:
            if attempt < max_retries - 1:
                await asyncio.sleep(1)
                continue
            return {
                'translated_text': 'Network error during translation. Please try again later.',
                'src': 'unknown',
                'dest': dest_lang,
                'confidence': 0
            }
        except Exception as e:
            if attempt < max_retries - 1:
                await asyncio.sleep(1)
                continue
            return {
                'translated_text': 'Translation service is currently unavailable. Please try again later.',
                'src': 'unknown',
                'dest': dest_lang,
                'confidence': 0
            }