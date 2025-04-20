from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render
from django.http import JsonResponse
from .models import OCRTest, TranslatorTest
from .services import detect_text
from translator.services import translate_text, get_available_languages
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
                
                # Read the image data
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

@admin.register(TranslatorTest)
class TranslatorTestAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'ocr_test', 'target_language', 'result_preview', 'error_message')
    readonly_fields = ('ocr_test', 'target_language', 'result', 'error_message', 'created_at')
    
    def result_preview(self, obj):
        if not obj.result:
            return '-'
        try:
            result = json.loads(obj.result)
            return f"Translated: {result.get('translated_text', '')[:100]}..."
        except json.JSONDecodeError:
            return 'Invalid JSON result'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('test/', self.test_view, name='ocr-translator-test'),
        ]
        return custom_urls + urls
    
    def test_view(self, request):
        if request.method == 'POST':
            try:
                ocr_test_id = request.POST.get('ocr_test')
                target_language = request.POST.get('target_language')
                
                if not ocr_test_id or not target_language:
                    return JsonResponse({'error': 'OCR test and target language are required'}, status=400)
                
                ocr_test = OCRTest.objects.get(id=ocr_test_id)
                if not ocr_test.result:
                    return JsonResponse({'error': 'Selected OCR test has no result'}, status=400)
                
                # Translate the text
                result = translate_text(ocr_test.result, target_language)
                
                # Create a new translator test record
                translator_test = TranslatorTest.objects.create(
                    ocr_test=ocr_test,
                    target_language=target_language,
                    result=json.dumps(result)
                )
                
                return JsonResponse({
                    'success': True,
                    'test_id': translator_test.id
                })
                
            except OCRTest.DoesNotExist:
                return JsonResponse({'error': 'OCR test not found'}, status=404)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
        
        # GET request - show the form
        # Get all OCR tests, ordered by creation date
        ocr_tests = OCRTest.objects.all().order_by('-created_at')
        
        # Get languages using the translator service
        languages = get_available_languages()
        
        context = {
            'ocr_tests': ocr_tests,
            'languages': languages,
            'title': 'Translation Test',
            'opts': self.model._meta,
        }
        
        return render(request, 'admin/ocr/translatortest/change_list.html', context)
