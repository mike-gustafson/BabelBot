import os
import json
import logging
from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.conf import settings
from .services import detect_text, detect_language

# Configure logging
logger = logging.getLogger('ocr_admin')

class OCRAdminView(View):
    template_name = 'ocr/admin.html'
    
    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        try:
            if 'image' not in request.FILES:
                return JsonResponse({
                    'status': 'error',
                    'message': 'No image file provided'
                })
            
            # Save the uploaded file temporarily
            image_file = request.FILES['image']
            temp_path = os.path.join(settings.MEDIA_ROOT, 'temp', image_file.name)
            os.makedirs(os.path.dirname(temp_path), exist_ok=True)
            
            with open(temp_path, 'wb+') as destination:
                for chunk in image_file.chunks():
                    destination.write(chunk)
            
            # Log the start of processing
            logger.info(f"Processing image: {image_file.name}")
            
            # Process the image
            result = detect_text(temp_path)
            
            # Log the result
            logger.info(f"OCR Result: {json.dumps(result, indent=2)}")
            
            # Clean up the temporary file
            os.remove(temp_path)
            
            return JsonResponse({
                'status': 'success',
                'result': result
            })
            
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })

class OCRLogsView(View):
    def get(self, request):
        # Get the last 100 log entries
        log_file = os.path.join(settings.BASE_DIR, 'logs', 'ocr_admin.log')
        logs = []
        
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                logs = f.readlines()[-100:]  # Get last 100 lines
        
        return JsonResponse({
            'logs': logs
        }) 