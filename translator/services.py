from googletrans import Translator
import asyncio
import logging
import time
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)

async def translate_text(text, dest_lang='en', max_retries=3):
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempting translation (attempt {attempt + 1}/{max_retries})")
            translator = Translator()
            
            # Set a longer timeout for Heroku
            translator.timeout = 10
            
            translation = translator.translate(text, dest=dest_lang)
            
            # If it's a coroutine, await it
            if asyncio.iscoroutine(translation):
                translation = await translation
            
            return translation.text
            
        except RequestException as e:
            logger.warning(f"Network error during translation (attempt {attempt + 1}): {str(e)}")
            if attempt < max_retries - 1:
                await asyncio.sleep(1)  # Wait before retrying
                continue
            logger.error("Max retries reached for translation")
            return "Network error during translation. Please try again later."
            
        except Exception as e:
            logger.error(f"Translation error: {str(e)}", exc_info=True)
            logger.error(f"Error type: {type(e)}")
            logger.error(f"Error args: {e.args}")
            return "Translation service is currently unavailable. Please try again later."
    
    return "Translation service is currently unavailable. Please try again later."