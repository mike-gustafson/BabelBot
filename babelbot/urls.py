from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main_app.urls')),
    path('translator/', include('translator.urls')),
    path('tts/', include('tts.urls')),
    path('ocr/', include('ocr.urls')),
]
