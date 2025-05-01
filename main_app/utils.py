from django.utils import timezone
from .models import Profile

def get_or_create_profile(user):
    """Get or create user profile"""
    profile, created = Profile.objects.get_or_create(user=user)
    return profile

def update_primary_language(user, language):
    """Update user's primary language"""
    profile = get_or_create_profile(user)
    profile.primary_language = language
    profile.save()
    return profile

def get_primary_language(user):
    """Get user's primary language"""
    profile = get_or_create_profile(user)
    return profile.primary_language

def update_other_languages(user, languages):
    """Update user's other known languages"""
    profile = get_or_create_profile(user)
    profile.other_languages = languages
    profile.save()
    return profile

def get_other_languages(user):
    """Get user's other known languages"""
    profile = get_or_create_profile(user)
    return profile.other_languages

def update_preferred_languages(user, languages):
    """Update user's preferred target languages for translation"""
    profile = get_or_create_profile(user)
    profile.preferred_languages = languages
    profile.save()
    return profile

def get_preferred_languages(user):
    """Get user's preferred target languages for translation"""
    profile = get_or_create_profile(user)
    return profile.preferred_languages

def get_all_user_languages(user):
    """Get all languages associated with a user (primary + other)"""
    profile = get_or_create_profile(user)
    languages = []
    if profile.primary_language:
        languages.append(profile.primary_language)
    if profile.other_languages:
        languages.extend(profile.other_languages)
    return list(set(languages))  # Remove duplicates 