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

class OCR(models.Model):
    result = models.JSONField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"OCR {self.id} - {self.created_at}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'OCR'
        verbose_name_plural = 'OCR'

class OCRTranslate(models.Model):
    image = models.ImageField(upload_to='ocr_translate_tests/')
    target_language = models.CharField(max_length=10)
    original_text = models.TextField(null=True, blank=True)
    detected_language = models.CharField(max_length=10, null=True, blank=True)
    translated_text = models.TextField(null=True, blank=True)
    processing_time = models.FloatField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"OCR Translate Test {self.id} - {self.created_at}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'OCR Translate Test'
        verbose_name_plural = 'OCR Translate Tests'