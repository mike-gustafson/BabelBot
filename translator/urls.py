from django.urls import path
from . import views

app_name = 'translator'

urlpatterns = [
    path('tech-demo/', views.tech_demo, name='tech_demo'),
    path('languages/', views.get_languages, name='get_languages'),
    path('translate/', views.translate_api, name='translate_api'),
] 