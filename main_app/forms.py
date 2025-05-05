from django import forms
from googletrans import LANGUAGES
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

class TranslateFromTextForm(forms.Form):
    text_to_translate = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 4,
            'required': True,
            'id': 'original_text',
            'class': 'form-input',
            'placeholder': 'Enter text to translate'
        }),
        label=''
    )
    
    target_language = forms.ChoiceField(
        choices=[('', 'Select a language')],
        widget=forms.Select(attrs={
            'id': 'language-select',
            'class': 'form-input',
            'required': True
        }),
        label=''
    )

    def __init__(self, *args, **kwargs):
        selected_language = kwargs.pop('selected_language', None)
        languages = kwargs.pop('languages', None)
        super().__init__(*args, **kwargs)
        
        if languages:
            self.fields['target_language'].choices = [('', 'Select a language')] + [(code, name.title()) for code, name in languages.items()]
        
        if selected_language:
            self.fields['target_language'].initial = selected_language

class TranslateFromOCRForm(forms.Form):
    image = forms.ImageField(
        widget=forms.FileInput(attrs={
            'id': 'ocr-image-input',
            'class': 'form-input',
            'accept': 'image/*',
            'required': True
        }),
        label=''
    )
    
    target_language = forms.ChoiceField(
        choices=[('', 'Select a language')],
        widget=forms.Select(attrs={
            'id': 'language-select',
            'class': 'form-input',
            'required': True
        }),
        label=''
    )

    def __init__(self, *args, **kwargs):
        selected_language = kwargs.pop('selected_language', None)
        languages = kwargs.pop('languages', None)
        super().__init__(*args, **kwargs)
        
        if languages:
            self.fields['target_language'].choices = [('', 'Select a language')] + [(code, name.title()) for code, name in languages.items()]
        
        if selected_language:
            self.fields['target_language'].initial = selected_language

class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Username',
            'autocomplete': 'username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Password',
            'autocomplete': 'current-password'
        })
    )

class SignupForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Email',
            'autocomplete': 'email'
        })
    )
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Username',
            'autocomplete': 'username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Password',
            'autocomplete': 'new-password'
        })
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Confirm Password',
            'autocomplete': 'new-password'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise ValidationError("Passwords do not match")
        
        return cleaned_data 

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        })
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a username'
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email address is already in use.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("This username is already taken.")
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user 

# Create a list of tuples for language choices
LANGUAGE_CHOICES = [(code, name.title()) for code, name in LANGUAGES.items()]
LANGUAGE_CHOICES.sort(key=lambda x: x[1])  # Sort by language name

class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    primary_language = forms.ChoiceField(
        choices=[('', 'Select a language')] + LANGUAGE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control language-select',
            'data-placeholder': 'Select primary language'
        })
    )
    other_languages = forms.MultipleChoiceField(
        choices=LANGUAGE_CHOICES,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control language-select',
            'data-placeholder': 'Select other languages',
            'multiple': 'multiple'
        }),
        required=False
    )

    class Meta:
        model = Profile
        fields = ['bio', 'location', 'primary_language', 'other_languages']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'cols': 40, 'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'bio': 'About Me',
            'location': 'Location',
            'primary_language': 'Primary Language',
            'other_languages': 'Other Languages',
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        
        # Update user fields
        if self.user:
            self.user.first_name = self.cleaned_data.get('first_name', '')
            self.user.last_name = self.cleaned_data.get('last_name', '')
            self.user.email = self.cleaned_data.get('email', '')
            if commit:
                self.user.save()
        
        # Update profile fields
        if commit:
            profile.save()
            # Save many-to-many fields
            self.save_m2m()
        
        return profile 