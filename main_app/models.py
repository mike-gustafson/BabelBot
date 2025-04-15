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

    def __str__(self):
        return self.user.username
    

class Translation(models.Model):
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
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    
    def __str__(self):
        user_display = self.user.username if self.user else "Anonymous"
        return f"Translation {self.id} by {user_display}"