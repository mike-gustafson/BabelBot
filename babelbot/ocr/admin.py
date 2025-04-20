from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render
from django.http import JsonResponse
from django.template.response import TemplateResponse
from .models import OCRTest
from .services import detect_text
import json
import logging

logger = logging.getLogger('ocr_admin')

@admin.register(OCRTest)
class OCRTestAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'result_preview', 'error_message')
    readonly_fields = ('result', 'error_message', 'created_at')
    change_list_template = 'admin/ocr/ocrtest/change_list.html'
    
    def result_preview(self, obj):
        if obj.result:
            return format_html('<pre style="max-height: 100px; overflow: auto;">{}</pre>', 
                             json.dumps(obj.result, indent=2))
        return '-'
    result_preview.short_description = 'Result'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('test/', self.admin_site.admin_view(self.test_view), name='ocr-test'),
            path('logs/', self.admin_site.admin_view(self.logs_view), name='ocr-logs'),
        ]
        return custom_urls + urls
    
    def test_view(self, request):
        if request.method == 'POST':
            try:
                image = request.FILES.get('image')
                if not image:
                    return JsonResponse({'error': 'No image provided'}, status=400)
                
                # Log the start of processing
                logger.info(f"Processing image: {image.name}")
                
                # Save the test record
                test = OCRTest.objects.create(image=image)
                
                # Process the image
                result = detect_text(test.image.path)
                
                # Log the result
                logger.info(f"OCR Result: {json.dumps(result, indent=2)}")
                
                # Update the test record
                test.result = result
                test.save()
                
                return JsonResponse({
                    'status': 'success',
                    'result': result
                })
                
            except Exception as e:
                logger.error(f"Error processing image: {str(e)}")
                test.error_message = str(e)
                test.save()
                return JsonResponse({'error': str(e)}, status=500)
        
        context = {
            'title': 'OCR Test',
            'opts': self.model._meta,
            'has_view_permission': self.has_view_permission(request),
        }
        return TemplateResponse(request, 'admin/ocr/ocrtest/test.html', context)
    
    def logs_view(self, request):
        # Get the last 100 log entries
        log_file = 'logs/ocr_admin.log'
        logs = []
        
        try:
            with open(log_file, 'r') as f:
                logs = f.readlines()[-100:]  # Get last 100 lines
        except FileNotFoundError:
            pass
        
        return JsonResponse({'logs': logs}) 