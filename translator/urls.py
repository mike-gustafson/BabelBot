from django.urls import path
from . import views

app_name = 'translator'

urlpatterns = [
    path('', views.translate_view, name='translate'),
    path('api/translate/', views.translate_api, name='translate_api'),
] 