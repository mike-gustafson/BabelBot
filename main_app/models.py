from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

#extend auth_user model
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    primary_language = models.CharField(max_length=30, blank=True)
    other_languages = models.CharField(max_length=30, blank=True)
    is_anonymous = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s profile"
    

class Translation(models.Model):
    REQUEST_TYPES = [
        ('typed', 'Typed'),
        ('ocr', 'OCR'),
    ]
    
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    original_text = models.TextField()
    translated_text = models.TextField()
    target_lang = models.CharField(max_length=10)
    request_type = models.CharField(max_length=10, choices=REQUEST_TYPES, default='typed')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        user_display = self.user.username if self.user else "Anonymous"
        return f"Translation {self.id} by {user_display}"

class OCRUsage(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ocr_usage'
    )
    month = models.DateField()  # Will store the first day of each month
    usage_count = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ('user', 'month')
        
    def __str__(self):
        return f"{self.user.username}'s OCR usage for {self.month.strftime('%B %Y')}"