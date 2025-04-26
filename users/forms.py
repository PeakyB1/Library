from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='', widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Логин'})
    )
    password = forms.CharField(
        label='', widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Пароль'})
    )

class RegisterForm(UserCreationForm):
    username = forms.CharField(
        label='', widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Логин'})
    )
    password1 = forms.CharField(
        label='', widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Пароль'})
    )
    password2 = forms.CharField(
        label='', widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Подтверждение пароля'})
    )
    error_messages = {
        'password_mismatch': "Пароли не совпадают.",
        }
    class Meta:
        model = get_user_model()
        fields = ['username','email', 'password1', 'password2']
        labels = {
            'first_name': '',
            'last_name': '',
            'email': '',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Имя'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Фамилия'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email'}),
        }
        