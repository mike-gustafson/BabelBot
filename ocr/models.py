from django.db import models
from django.utils import timezone

# Create your models here.

class OCRTest(models.Model):
    image = models.ImageField(upload_to='ocr_tests/', null=True, blank=True)
    result = models.JSONField(null=True, blank=True, default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    error_message = models.TextField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"OCR Test {self.id} - {self.created_at}"
