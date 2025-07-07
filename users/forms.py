from django import forms
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.core.exceptions import ValidationError
from django_countries.widgets import CountrySelectWidget

from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("email", "username", "avatar", "phone", "country")
        widgets = {
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "avatar": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "country": forms.Select(attrs={"class": "form-select"}),
        }


class CustomUserChangeForm(UserChangeForm):
    password = None  # скрываем поле пароля

    class Meta:
        model = CustomUser
        fields = ("email", "avatar", "phone", "country")
        widgets = {
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "avatar": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "country": CountrySelectWidget(attrs={"class": "form-select"}),
        }


# ✅ Кастомная форма входа с проверкой блокировки
class CustomAuthenticationForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        if user.is_blocked:
            messages.error(self.request, "Ваш аккаунт заблокирован.")  # ✅ всплывающее сообщение
            raise ValidationError("", code="blocked")  # пустая ошибка, чтобы остановить вход
