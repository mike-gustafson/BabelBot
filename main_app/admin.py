from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.urls import path
from django.shortcuts import render
from .models import Translation, Profile

class CustomAdminSite(admin.AdminSite):
    def get_app_list(self, request):
        app_list = super().get_app_list(request)
        return app_list

# Create custom admin site
admin_site = CustomAdminSite(name='admin')

# Register models with the custom admin site
@admin.register(Translation, site=admin_site)
class TranslationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'target_language', 'created_at', 'truncated_original_text', 'truncated_translated_text')
    list_filter = ('target_language', 'created_at', 'user')
    search_fields = ('original_text', 'translated_text', 'user__username')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    def truncated_original_text(self, obj):
        return obj.original_text[:50] + '...' if len(obj.original_text) > 50 else obj.original_text
    truncated_original_text.short_description = 'Original Text'
    
    def truncated_translated_text(self, obj):
        return obj.translated_text[:50] + '...' if len(obj.translated_text) > 50 else obj.translated_text
    truncated_translated_text.short_description = 'Translated Text'

@admin.register(Profile, site=admin_site)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'primary_language', 'other_languages', 'location')
    search_fields = ('user__username', 'primary_language', 'other_languages', 'location')

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_primary_language')
    list_select_related = ('profile',)

    def get_primary_language(self, instance):
        return instance.profile.primary_language
    get_primary_language.short_description = 'Primary Language'

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)

# Register User model with the custom admin site
admin_site.register(User, CustomUserAdmin)

# Replace the default admin site with our custom one
admin.site = admin_site
