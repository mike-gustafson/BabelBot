from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Translation, Profile

@admin.register(Translation)
class TranslationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'target_lang', 'created_at', 'truncated_original_text', 'truncated_translated_text')
    list_filter = ('target_lang', 'created_at', 'user')
    search_fields = ('original_text', 'translated_text', 'user__username')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    def truncated_original_text(self, obj):
        return obj.original_text[:50] + '...' if len(obj.original_text) > 50 else obj.original_text
    truncated_original_text.short_description = 'Original Text'
    
    def truncated_translated_text(self, obj):
        return obj.translated_text[:50] + '...' if len(obj.translated_text) > 50 else obj.translated_text
    truncated_translated_text.short_description = 'Translated Text'

@admin.register(Profile)
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

# Unregister the default User admin and register our custom admin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
