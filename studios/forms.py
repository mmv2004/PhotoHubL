from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.validators import URLValidator
from .models import Studio, StudioImage

class StudioForm(forms.ModelForm):
    """
    Форма для создания и редактирования студий/локаций
    """
    class Meta:
        model = Studio
        fields = ['name', 'location_type', 'full_address', 'city', 'district', 'website', 'description', 'latitude', 'longitude', 'is_public']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название студии или локации'}),
            'location_type': forms.Select(attrs={'class': 'form-select'}),
            'full_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Полный адрес', 'readonly': 'readonly', 'id': 'id_full_address'}),
            'city': forms.HiddenInput(),
            'district': forms.HiddenInput(),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Описание студии, особенности, условия аренды и т.д.'}),
            'latitude': forms.HiddenInput(attrs={'id': 'id_latitude'}),
            'longitude': forms.HiddenInput(attrs={'id': 'id_longitude'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_website(self):
        """
        Проверка формата веб-сайта
        """
        website = self.cleaned_data.get('website')
        if website:
            try:
                URLValidator()(website)
            except forms.ValidationError:
                if not website.startswith(('http://', 'https://')):
                    website = 'https://' + website
                    try:
                        URLValidator()(website)
                    except forms.ValidationError:
                        raise forms.ValidationError(_('Введите корректный URL'))
        return website

class StudioImageForm(forms.ModelForm):
    """
    Форма для добавления изображений студии
    """
    class Meta:
        model = StudioImage
        fields = ['image', 'caption', 'is_main']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'caption': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Подпись к изображению (необязательно)'}),
            'is_main': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_image(self):
        """
        Проверка размера изображения
        """
        image = self.cleaned_data.get('image')
        if image:
            if image.size > 5 * 1024 * 1024:  # 5 МБ
                raise forms.ValidationError(_('Размер изображения не должен превышать 5 МБ'))
        return image

class StudioSearchForm(forms.Form):
    """
    Форма для поиска студий
    """
    query = forms.CharField(
        label=_('Поиск'),
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Поиск студий...'})
    )
    location_type = forms.ChoiceField(
        label=_('Тип локации'),
        choices=[('all', 'Все типы')] + list(Studio.LOCATION_TYPE_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    city = forms.CharField(
        label=_('Город'),
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Город'})
    )

