from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render
from django.http import JsonResponse
from .models import OCRTest
from .services import detect_text
from translator.services import get_available_languages, translate_text
import json
from main_app.admin import admin_site

@admin.register(OCRTest, site=admin_site)
class OCRTestAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'result_preview', 'error_message')
    readonly_fields = ('created_at', 'result', 'error_message')
    ordering = ('-created_at',)
    
    def result_preview(self, obj):
        if obj.result:
            try:
                result_data = obj.result
                if isinstance(result_data, str):
                    result_data = json.loads(result_data)
                return format_html(
                    '<div style="max-width: 300px; overflow: hidden; text-overflow: ellipsis;">'
                    '<strong>Text:</strong> {}<br>'
                    '<strong>Language:</strong> {}'
                    '</div>',
                    result_data.get('full_text', '')[:100] + '...' if len(result_data.get('full_text', '')) > 100 else result_data.get('full_text', ''),
                    result_data.get('language', 'unknown')
                )
            except:
                return "Error parsing result"
        return ""
    result_preview.short_description = "Result"
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_test_form'] = True
        extra_context['languages'] = get_available_languages()
        return super().changelist_view(request, extra_context)
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('test/', self.test_view, name='ocr-test'),
            path('translate/', self.translate_view, name='ocr-translate'),
        ]
        return custom_urls + urls
    
    def test_view(self, request):
        if request.method == 'POST':
            try:
                image = request.FILES.get('image')
                if not image:
                    return JsonResponse({'error': 'No image provided'}, status=400)
                
                # Process the image
                image_data = image.read()
                result = detect_text(image_data)
                
                # Create a new OCRTest record
                OCRTest.objects.create(result=json.dumps(result))
                
                return JsonResponse({'success': True, 'result': result})
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
        return render(request, 'admin/ocr/ocr-and-translate-test/change_list.html')
    
    def translate_view(self, request):
        if request.method == 'POST':
            try:
                source_text = request.POST.get('source_text')
                target_language = request.POST.get('target_language')
                
                if not source_text or not target_language:
                    return JsonResponse({'error': 'Source text and target language are required'}, status=400)
                
                # Translate the text
                result = translate_text(source_text, target_language)
                
                return JsonResponse({'success': True, 'result': result})
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
        return JsonResponse({'error': 'Method not allowed'}, status=405)
