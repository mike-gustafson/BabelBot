from django.urls import path
from . import views

urlpatterns = [
    path('process/', views.process_image, name='process_image'),
    path('api/ocr/', views.perform_ocr, name='perform_ocr'),
    path('api/ocr-translate/', views.perform_ocr_translate, name='perform_ocr_translate'),
] 