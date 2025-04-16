from googletrans import Translator
import asyncio
import logging

logger = logging.getLogger(__name__)

def translate_text(text, dest_lang='en'):
    try:
        translator = Translator()
        translation = translator.translate(text, dest=dest_lang)

        # Handle async coroutine if needed
        if asyncio.iscoroutine(translation):
            translation = asyncio.run(translation)

        return translation.text
    except Exception as e:
        logger.error(f"Translation error: {str(e)}", exc_info=True)
        raise Exception("Translation service is currently unavailable. Please try again later.")