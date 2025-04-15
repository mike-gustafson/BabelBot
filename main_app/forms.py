from django import forms
from googletrans import LANGUAGES

class TranslationForm(forms.Form):
    text_to_translate = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 4,
            'required': True,
            'id': 'text_to_translate',
            'class': 'form-control'
        }),
        label='Text to Translate'
    )
    
    target_language = forms.ChoiceField(
        choices=[('', 'Select a language')] + [(code, name.title()) for code, name in LANGUAGES.items()],
        widget=forms.Select(attrs={
            'id': 'language-select',
            'class': 'form-control',
            'required': True
        }),
        label='Target Language'
    )

    def __init__(self, *args, **kwargs):
        selected_language = kwargs.pop('selected_language', None)
        super().__init__(*args, **kwargs)
        if selected_language:
            self.fields['target_language'].initial = selected_language 