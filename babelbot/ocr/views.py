from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.conf import settings
from .services import detect_text

class OCRAdminView(View):
    def get(self, request):
        return render(request, 'admin/ocr/test.html')

    def post(self, request):
        try:
            result = detect_text(request.FILES['image'])
            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class OCRLogsView(View):
    def get(self, request):
        return render(request, 'admin/ocr/logs.html') 