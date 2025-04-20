from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render
from django.http import JsonResponse
from django.template.response import TemplateResponse
from .models import OCRTest
from .services import detect_text
import os
import json
import tempfile

@admin.register(OCRTest)
class OCRTestAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'result_preview', 'error_message')
    readonly_fields = ('result', 'error_message', 'created_at')
    
    def result_preview(self, obj):
        if not obj.result:
            return "-"
        try:
            result = obj.result
            if isinstance(result, str):
                result = json.loads(result)
            return format_html(
                '<div style="max-width: 300px; overflow: hidden; text-overflow: ellipsis;">'
                '<strong>Text:</strong> {}<br>'
                '<strong>Language:</strong> {}'
                '</div>',
                result.get('full_text', '')[:100] + '...' if len(result.get('full_text', '')) > 100 else result.get('full_text', ''),
                result.get('language', 'unknown')
            )
        except Exception as e:
            return f"Error displaying result: {str(e)}"
    result_preview.short_description = 'Result'
    
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
                
                # Read the image file into memory
                image_data = image.read()
                
                # Process the image
                result = detect_text(image_data)
                
                # Create a new OCRTest record without the image
                ocr_test = OCRTest.objects.create(
                    result=result
                )
                
                return JsonResponse({
                    'success': True,
                    'test_id': ocr_test.id,
                    'result': result
                })
                
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
        
        return TemplateResponse(request, 'admin/ocr/ocrtest/change_list.html', {
            'title': 'OCR Test',
            'opts': self.model._meta,
        })
