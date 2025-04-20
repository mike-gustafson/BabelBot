from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render
from django.http import JsonResponse
from .models import OCRTest
from .services import detect_text
import json

@admin.register(OCRTest)
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
        return super().changelist_view(request, extra_context)
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('test/', self.test_view, name='ocr-test'),
        ]
        return custom_urls + urls
    
    def test_view(self, request):
        if request.method == 'POST':
            try:
                image = request.FILES.get('image')
                if not image:
                    return JsonResponse({'error': 'No image provided'}, status=400)
                
                # Read the image data into memory
                image_data = image.read()
                
                # Process the image
                result = detect_text(image_data)
                
                # Create a new OCR test record
                ocr_test = OCRTest.objects.create(
                    result=json.dumps(result)
                )
                
                return JsonResponse({
                    'success': True,
                    'test_id': ocr_test.id,
                    'result': result
                })
                
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
        
        return render(request, 'admin/ocr/ocrtest/change_list.html', {
            'title': 'OCR Test',
            'opts': self.model._meta,
        })
