from django.db import models
from django.utils import timezone

# Create your models here.

class TranslationTest(models.Model):
    source_text = models.TextField()
    target_language = models.CharField(max_length=10)
    result = models.JSONField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Translation Test {self.id} ({self.created_at})"
