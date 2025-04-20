from datetime import datetime
from django.utils import timezone
from .models import OCRUsage

def get_or_create_ocr_usage(user):
    """Get or create OCR usage record for the current month"""
    current_month = timezone.now().replace(day=1)
    usage, created = OCRUsage.objects.get_or_create(
        user=user,
        month=current_month,
        defaults={'usage_count': 0}
    )
    return usage

def increment_ocr_usage(user):
    """Increment OCR usage count for the current month"""
    usage = get_or_create_ocr_usage(user)
    usage.usage_count += 1
    usage.save()
    return usage.usage_count

def get_ocr_usage_count(user):
    """Get current month's OCR usage count"""
    usage = get_or_create_ocr_usage(user)
    return usage.usage_count

def can_use_ocr(user):
    """Check if user can perform OCR (not anonymous and under monthly limit)"""
    if user.profile.is_anonymous:
        return False
    return get_ocr_usage_count(user) < 1000 