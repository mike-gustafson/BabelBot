import asyncio
from googletrans import Translator

async def translate_text(text, dest_lang='en'):
    translator = Translator()
    translation = await translator.translate(text, dest=dest_lang)
    return translation.text
