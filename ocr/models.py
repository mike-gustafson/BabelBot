from django.db import models
import json

# Create your models here.

class OCRTest(models.Model):
    result = models.JSONField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"OCR Test {self.id} - {self.created_at}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'OCR Test'
        verbose_name_plural = 'OCR Tests'