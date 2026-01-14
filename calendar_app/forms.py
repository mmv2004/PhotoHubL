from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta

from .models import Event
from clients.models import Client
from studios.models import Studio

class EventForm(forms.ModelForm):
    """
    Форма для создания и редактирования событий
    """
    class Meta:
        model = Event
        fields = ['title',  'start_datetime', 'end_datetime', 'client', 'studio', 'description', 'is_all_day', 'color']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название события'}),
            'start_datetime': forms.DateTimeInput(attrs={'class': 'form-control datepicker', 'placeholder': 'Дата и время начала'}),
            'end_datetime': forms.DateTimeInput(attrs={'class': 'form-control datepicker', 'placeholder': 'Дата и время окончания'}),
            'client': forms.Select(attrs={'class': 'form-select'}),
            'studio': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Описание события (необязательно)'}),
            'is_all_day': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Устанавливаем начальные значения для дат, если это новое событие
        if not self.instance.pk:
            now = timezone.now()
            rounded_now = now.replace(minute=0 if now.minute < 30 else 30, second=0, microsecond=0)
            if now.minute < 30:
                rounded_now = rounded_now.replace(minute=30)
            else:
                rounded_now = rounded_now + timedelta(hours=1)
                rounded_now = rounded_now.replace(minute=0)
            
            self.initial['start_datetime'] = rounded_now
            self.initial['end_datetime'] = rounded_now + timedelta(hours=1)

        # Фильтруем клиентов и студии по пользователю, если он передан
        if user:
            self.fields['client'].queryset = Client.objects.filter(photographer=user)
            self.fields['studio'].queryset = Studio.objects.filter(is_public=True) | Studio.objects.filter(created_by=user)
    
    def clean(self):
        """
        Проверка корректности данных формы
        """
        cleaned_data = super().clean()
        start_datetime = cleaned_data.get('start_datetime')
        end_datetime = cleaned_data.get('end_datetime')
        is_all_day = cleaned_data.get('is_all_day')
        
        if start_datetime and end_datetime:
            # Если событие на весь день, устанавливаем время начала на 00:00 и время окончания на 23:59
            if is_all_day:
                start_datetime = start_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
                end_datetime = end_datetime.replace(hour=23, minute=59, second=59, microsecond=999999)
                cleaned_data['start_datetime'] = start_datetime
                cleaned_data['end_datetime'] = end_datetime

            # Проверяем, что дата окончания не раньше даты начала
            if end_datetime < start_datetime:
                self.add_error('end_datetime', _('Дата и время окончания не может быть раньше даты и времени начала'))

        if start_datetime:
            if start_datetime < timezone.now():
                self.add_error('start_datetime', _('Дата и время начала не может быть раньше даты и времени текущего момента'))

        return cleaned_data


class EventFormPost(forms.ModelForm):
    """
    Форма для создания и редактирования событий
    """

    class Meta:
        model = Event
        fields = ['title', 'start_datetime', 'end_datetime', 'description',
                  'is_all_day', 'color']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название события'}),
            'start_datetime': forms.DateTimeInput(
                attrs={'class': 'form-control datepicker', 'placeholder': 'Дата и время начала'}),
            'end_datetime': forms.DateTimeInput(
                attrs={'class': 'form-control datepicker', 'placeholder': 'Дата и время окончания'}),
            'description': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Описание события (необязательно)'}),
            'is_all_day': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Устанавливаем начальные значения для дат, если это новое событие
        if not self.instance.pk:
            now = timezone.now()
            rounded_now = now.replace(minute=0 if now.minute < 30 else 30, second=0, microsecond=0)
            if now.minute < 30:
                rounded_now = rounded_now.replace(minute=30)
            else:
                rounded_now = rounded_now + timedelta(hours=1)
                rounded_now = rounded_now.replace(minute=0)

            self.initial['start_datetime'] = rounded_now
            self.initial['end_datetime'] = rounded_now + timedelta(hours=1)




    def clean(self):
        """
        Проверка корректности данных формы
        """
        cleaned_data = super().clean()
        start_datetime = cleaned_data.get('start_datetime')
        end_datetime = cleaned_data.get('end_datetime')
        is_all_day = cleaned_data.get('is_all_day')

        if start_datetime and end_datetime:
            # Если событие на весь день, устанавливаем время начала на 00:00 и время окончания на 23:59
            if is_all_day:
                start_datetime = start_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
                end_datetime = end_datetime.replace(hour=23, minute=59, second=59, microsecond=999999)
                cleaned_data['start_datetime'] = start_datetime
                cleaned_data['end_datetime'] = end_datetime

            # Проверяем, что дата окончания не раньше даты начала
            if end_datetime < start_datetime:
                self.add_error('end_datetime', _('Дата и время окончания не может быть раньше даты и времени начала'))

        if start_datetime:
            if start_datetime < timezone.now():
                self.add_error('start_datetime', _('Дата и время окончания не может быть раньше даты и времени начала'))

        return cleaned_data