from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm, SetPasswordForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import CustomUser
from datetime import date
from dateutil.relativedelta import relativedelta


class CustomUserCreationForm(UserCreationForm):
    """
    Форма для создания нового пользователя с дополнительными полями
    """
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
    )
    first_name = forms.CharField(
        label=_("Имя"),
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя'}),
    )
    last_name = forms.CharField(
        label=_("Фамилия"),
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Фамилия'}),
    )
    birth_date = forms.DateField(
        label=_("Дата рождения"),
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=False,
    )
    phone_number = forms.CharField(
        label=_("Телефон"),
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Телефон'}),
    )
    avatar = forms.ImageField(
        label=_("Аватар"),
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        required=False,
    )
    password1 = forms.CharField(
        label=_("Пароль"),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Пароль'}),
    )
    password2 = forms.CharField(
        label=_("Подтверждение пароля"),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Подтверждение пароля'}),
    )

    class Meta:
        model = CustomUser
        fields = (
            'email', 'username', 'first_name', 'last_name',
            'birth_date', 'phone_number', 'avatar',
            'password1', 'password2'
        )
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя пользователя'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.birth_date = self.cleaned_data.get('birth_date')
        user.phone_number = self.cleaned_data.get('phone_number')
        user.avatar = self.cleaned_data.get('avatar')
        if commit:
            user.save()
        return user

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        max_birth_date = date.today() - relativedelta(years=14)
        self.fields['birth_date'].widget.attrs['max'] = max_birth_date.strftime('%Y-%m-%d')

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date:
            today = date.today()
            age = today.year - birth_date.year - (
                    (today.month, today.day) < (birth_date.month, birth_date.day)
            )
            if age < 14:
                raise ValidationError("Клиент должен быть не младше 14 лет.")
        return birth_date


class CustomUserChangeForm(UserChangeForm):
    """
    Форма для изменения данных пользователя
    """
    password = None  # Удаляем поле пароля из формы

    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'birth_date', 'phone_number', 'avatar')
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
        }


class CustomAuthenticationForm(AuthenticationForm):
    """
    Форма для аутентификации пользователя
    """
    username = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
    )
    password = forms.CharField(
        label=_("Пароль"),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Пароль'}),
    )


class CustomSetPasswordForm(SetPasswordForm):
    """
    Форма для установки нового пароля
    """
    new_password1 = forms.CharField(
        label=_("Новый пароль"),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Новый пароль'}),
    )
    new_password2 = forms.CharField(
        label=_("Подтверждение нового пароля"),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Подтверждение нового пароля'}),
    )


# НОВЫЕ ФОРМЫ ДЛЯ ПОДТВЕРЖДЕНИЯ EMAIL И ВОССТАНОВЛЕНИЯ ПАРОЛЯ

class EmailConfirmationForm(forms.Form):
    """
    Форма для ввода кода подтверждения Email.
    """
    confirmation_code = forms.CharField(
        label=_("Код подтверждения"),
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите 6-значный код',
            'autocomplete': 'off'
        }),
        help_text=_("Код отправлен на ваш Email.")
    )


class PasswordResetRequestForm(forms.Form):
    """
    Форма для запроса сброса пароля по Email.
    """
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите ваш Email'
        }),
    )


class PasswordResetConfirmForm(forms.Form):
    """
    Форма для ввода кода подтверждения и установки нового пароля.
    """
    confirmation_code = forms.CharField(
        label=_("Код подтверждения"),
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите 6-значный код',
            'autocomplete': 'off'
        }),
        help_text=_("Код отправлен на ваш Email.")
    )
    new_password1 = forms.CharField(
        label=_("Новый пароль"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Новый пароль'
        }),
    )
    new_password2 = forms.CharField(
        label=_("Подтверждение нового пароля"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Подтверждение нового пароля'
        }),
    )

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("new_password1")
        password2 = cleaned_data.get("new_password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError(_("Пароли не совпадают."))

        return cleaned_data