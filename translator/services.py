from googletrans import Translator

def translate_text(text, dest_lang='en'):
    translator = Translator()
    translation = translator.translate(text, dest=dest_lang)
    return translation.text
