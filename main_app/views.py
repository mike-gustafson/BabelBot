from django.http import HttpResponse
from translator.services import translate_text

async def home(request):
    original_text = "Bonjour tout le monde!"
    translated_text = await translate_text(original_text, 'es')
    return HttpResponse(f'<h1>Welcome to BableBot 1.0</h1><h2>{translated_text}</h2>')
