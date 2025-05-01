from django.urls import path
from . import views

app_name = 'tts'

urlpatterns = [
    path('tech-demo/', views.tech_demo, name='tech_demo'),
    path('languages/', views.get_languages, name='get_languages'),
    path('generate/', views.generate_speech, name='generate_speech'),
] 