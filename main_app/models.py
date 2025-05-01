from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings
from django.utils import timezone

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
    other_languages = models.JSONField(default=list)
    preferred_languages = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Translation(models.Model):
    TRANSLATION_TYPES = [
        ('typed', 'Typed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    original_text = models.TextField()
    translated_text = models.TextField()
    target_language = models.CharField(max_length=10)
    translation_type = models.CharField(max_length=10, choices=TRANSLATION_TYPES, default='typed')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Translation by {self.user.username if self.user else 'Anonymous'} at {self.created_at}"