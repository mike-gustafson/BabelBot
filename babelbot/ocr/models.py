from django.db import models
from django.utils import timezone

class OCRTest(models.Model):
    image = models.ImageField(upload_to='ocr_tests/')
    result = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    error_message = models.TextField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"OCR Test {self.id} - {self.created_at}" 