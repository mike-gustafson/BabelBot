from django.db import models
from django.utils import timezone

# Create your models here.

class OCRTest(models.Model):
    image = models.ImageField(upload_to='ocr_tests/')
    result = models.JSONField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"OCR Test {self.id} ({self.created_at})"

class TranslatorTest(models.Model):
    ocr_test = models.ForeignKey(OCRTest, on_delete=models.CASCADE)
    target_language = models.CharField(max_length=10)
    result = models.JSONField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Translation Test {self.id} for OCR {self.ocr_test_id}"
