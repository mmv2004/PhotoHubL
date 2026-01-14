from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import Client
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta


class ClientForm(forms.ModelForm):
    """
    Форма для создания и редактирования клиентов
    """
    class Meta:
        model = Client
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'birth_date', 'address', 'notes']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя клиента'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Фамилия клиента'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+79991234567'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Адрес клиента'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Дополнительная информация о клиенте'}),
        }

    def clean_phone_number(self):
        """
        Проверка формата номера телефона
        """
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number and not phone_number.startswith('+'):
            phone_number = '+' + phone_number
        return phone_number

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        max_birth_date = date.today() - relativedelta(years=14)
        self.fields['birth_date'].widget.attrs['max'] = max_birth_date.strftime('%Y-%m-%d')

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date:
            today = date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            if age < 14:
                raise ValidationError("Клиент должен быть не младше 14 лет.")
        return birth_date



