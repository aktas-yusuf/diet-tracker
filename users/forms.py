from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    gender = forms.ChoiceField(
        choices=[('', 'Seçiniz')] + list(CustomUser.GENDER_CHOICES),
        required=False,
        label='Cinsiyet',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    activity_level = forms.ChoiceField(
        choices=[('', 'Seçiniz')] + list(CustomUser.ACTIVITY_LEVELS),
        required=False,
        label='Aktivite Seviyesi',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'age', 'height', 'weight',
            'gender', 'activity_level', 'password1', 'password2'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Labels
        self.fields['username'].label = 'Kullanıcı Adı'
        self.fields['email'].label = 'E-posta'
        self.fields['age'].label = 'Yaş'
        self.fields['height'].label = 'Boy (cm)'
        self.fields['weight'].label = 'Kilo (kg)'
        self.fields['gender'].label = 'Cinsiyet'
        self.fields['activity_level'].label = 'Aktivite Seviyesi'
        self.fields['password1'].label = 'Şifre'
        self.fields['password2'].label = 'Şifre (Tekrar)'

        
        self.fields['username'].widget = forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Kullanıcı adınız'}
        )
        self.fields['email'].widget = forms.EmailInput(
            attrs={'class': 'form-control', 'placeholder': 'E-posta adresiniz'}
        )
        self.fields['age'].widget = forms.NumberInput(
            attrs={'class': 'form-control', 'min': '1', 'max': '120'}
        )
        self.fields['height'].widget = forms.NumberInput(
            attrs={'class': 'form-control', 'step': '0.1', 'min': '100', 'max': '250'}
        )
        self.fields['weight'].widget = forms.NumberInput(
            attrs={'class': 'form-control', 'step': '0.1', 'min': '20', 'max': '300'}
        )
        self.fields['gender'].disabled = False
        self.fields['activity_level'].disabled = False

        self.fields['gender'].widget = forms.Select(
            attrs={'class': 'form-select'}
        )
        self.fields['activity_level'].widget = forms.Select(
            attrs={'class': 'form-select'}
        )
        self.fields['password1'].widget = forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Şifrenizi girin'}
        )
        self.fields['password2'].widget = forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Şifrenizi tekrar girin'}
        )

    def clean_gender(self):
        value = self.cleaned_data.get('gender')
        return value or None

    def clean_activity_level(self):
        value = self.cleaned_data.get('activity_level')
        return value or None


class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Treat username as email 
        self.fields['username'].label = 'E-posta'
        self.fields['username'].widget = forms.EmailInput(
            attrs={'class': 'form-control', 'placeholder': 'E-posta adresi'}
        )
        self.fields['password'].label = 'Şifre'
        self.fields['password'].widget = forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Şifreniz'}
        )
