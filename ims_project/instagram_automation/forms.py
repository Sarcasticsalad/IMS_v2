from django import forms
from .models import InstagramCredentials

class InstagramCredentialsForm(forms.ModelForm):
    class Meta:
        model = InstagramCredentials
        fields = ['access_token', 'instagram_account_id']
        widgets = {
            'access_token': forms.TextInput(attrs={'class': 'form-control'}),
            'instagram_account_id': forms.TextInput(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'access_token': 'Your Instagram Graph API access token',
            'instagram_account_id': 'Your Instagram Business Account ID'
        } 