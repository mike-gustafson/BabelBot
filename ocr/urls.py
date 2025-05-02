from django.urls import path
from . import views

urlpatterns = [
    path('tech-demo/', views.tech_demo, name='ocr_tech_demo'),
    path('process/', views.perform_ocr, name='perform_ocr'),
] 