import asyncio
from googletrans import Translator

async def translate_text(text, dest_lang='en'):
    translator = Translator()
    # Await the translate call since it returns a coroutine.
    translation = await translator.translate(text, dest=dest_lang)
    return translation.text
