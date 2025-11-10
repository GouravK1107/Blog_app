from django import forms
from .models import *

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'name', 'bio', 'date_of_birth',
            'website', 'twitter', 'linkedin', 'github', 'instagram', 'profile_picture'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3, 'maxlength': 150, 'placeholder': 'Tell us about yourself...'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'website': forms.URLInput(attrs={'placeholder': 'https://yourwebsite.com'}),
            'twitter': forms.URLInput(attrs={'placeholder': 'https://twitter.com/username'}),
            'linkedin': forms.URLInput(attrs={'placeholder': 'https://linkedin.com/in/username'}),
            'github': forms.URLInput(attrs={'placeholder': 'https://github.com/username'}),
            'instagram': forms.URLInput(attrs={'placeholder': 'https://instagram.com/username'}),
        }
