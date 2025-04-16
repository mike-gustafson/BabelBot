from googletrans import Translator
import asyncio

def translate_text(text, dest_lang='en'):
    translator = Translator()
    translation = translator.translate(text, dest=dest_lang)

    # Handle async coroutine if needed
    if asyncio.iscoroutine(translation):
        translation = asyncio.run(translation)

    return translation.text