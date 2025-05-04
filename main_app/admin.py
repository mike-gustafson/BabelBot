from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Translation, Profile
from translator.services import get_available_languages

class CustomAdminSite(admin.AdminSite):
    site_header = 'BabelBot Administration'
    site_title = 'BabelBot Admin'
    index_title = 'Welcome to BabelBot Administration'

    def get_app_list(self, request):
        app_list = super().get_app_list(request)
        return app_list

# Create custom admin site
admin_site = CustomAdminSite(name='admin')

@admin.register(Translation, site=admin_site)
class TranslationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'target_language', 'translation_type', 'created_at', 
                   'truncated_original_text', 'truncated_translated_text')
    list_filter = ('target_language', 'translation_type', 'created_at', 'user')
    search_fields = ('original_text', 'translated_text', 'user__username', 'target_language')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    list_per_page = 20
    
    fieldsets = (
        ('Translation Details', {
            'fields': ('user', 'target_language', 'translation_type')
        }),
        ('Content', {
            'fields': ('original_text', 'translated_text')
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )
    
    def truncated_original_text(self, obj):
        return obj.original_text[:50] + '...' if len(obj.original_text) > 50 else obj.original_text
    truncated_original_text.short_description = 'Original Text'
    
    def truncated_translated_text(self, obj):
        return obj.translated_text[:50] + '...' if len(obj.translated_text) > 50 else obj.translated_text
    truncated_translated_text.short_description = 'Translated Text'

@admin.register(Profile, site=admin_site)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'primary_language', 'location', 
                   'is_anonymous', 'created_at', 'updated_at')
    list_filter = ('primary_language', 'is_anonymous', 
                  'created_at', 'updated_at')
    search_fields = ('user__username', 'primary_language', 
                    'location', 'bio')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    list_per_page = 20
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        languages = get_available_languages()
        language_choices = [(code, name.title()) for code, name in languages.items()]
        
        # Update primary language field
        form.base_fields['primary_language'].choices = [('', 'Select a language')] + language_choices
        
        # Update other languages field
        form.base_fields['other_languages'].choices = language_choices
        
        return form
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'is_anonymous')
        }),
        ('Language Preferences', {
            'fields': ('primary_language', 'other_languages')
        }),
        ('Profile Information', {
            'fields': ('bio', 'location')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'
    fields = ('primary_language', 'other_languages', 
              'bio', 'location', 'is_anonymous')
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        languages = get_available_languages()
        language_choices = [(code, name.title()) for code, name in languages.items()]
        
        # Update primary language field
        formset.form.base_fields['primary_language'].choices = [('', 'Select a language')] + language_choices
        
        # Update other languages field
        formset.form.base_fields['other_languages'].choices = language_choices
        
        return formset

class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 
                   'is_active', 'date_joined', 'get_primary_language')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    list_select_related = ('profile',)
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    list_per_page = 20

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
