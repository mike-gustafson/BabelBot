from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render
from django.http import JsonResponse
from .models import TranslationTest
from .services import translate_text, get_available_languages
import json
from asgiref.sync import sync_to_async, async_to_sync
from django.template.response import TemplateResponse
import asyncio

@admin.register(TranslationTest)
class TranslationTestAdmin(admin.ModelAdmin):
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
                    '<strong>Source ({}):</strong> {}<br>'
                    '<strong>Translated ({}):</strong> {}'
                    '</div>',
                    result_data.get('src', 'unknown'),
                    result_data.get('source_text', '')[:100] + '...' if len(result_data.get('source_text', '')) > 100 else result_data.get('source_text', ''),
                    result_data.get('dest', 'unknown'),
                    result_data.get('translated_text', '')[:100] + '...' if len(result_data.get('translated_text', '')) > 100 else result_data.get('translated_text', '')
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
            path('test/', self.test_view_wrapper, name='translator-test'),
        ]
        return custom_urls + urls
    
    @sync_to_async
    def _create_translation_test(self, source_text, target_language, result):
        return TranslationTest.objects.create(
            source_text=source_text,
            target_language=target_language,
            result=json.dumps(result)
        )
    
    @sync_to_async
    def _render_response(self, request, template, context):
        return TemplateResponse(request, template, context)
    
    async def test_view(self, request):
        if request.method == 'POST':
            try:
                source_text = request.POST.get('source_text')
                target_language = request.POST.get('target_language')
                
                if not source_text or not target_language:
                    return JsonResponse({'error': 'Source text and target language are required'}, status=400)
                
                # Translate the text
                result = await translate_text(source_text, target_language)
                
                # Create a new translation test record
                translation_test = await self._create_translation_test(
                    source_text=source_text,
                    target_language=target_language,
                    result=result
                )
                
                return JsonResponse({
                    'success': True,
                    'test_id': translation_test.id,
                    'result': result
                })
                
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
        
        # GET request - show the form
        languages = get_available_languages()
        return render(request, 'admin/translator/translationtest/change_list.html', {
            'languages': languages,
            'title': 'Translation Test',
            'opts': self.model._meta,
            'show_test_form': True
        })
    
    def test_view_wrapper(self, request):
        """Synchronous wrapper for the async view"""
        async def _wrapped():
            return await self.test_view(request)
        return async_to_sync(_wrapped)()
