from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.validators import URLValidator
from .models import ReferenceCategory, Reference

class CategoryForm(forms.ModelForm):
    """
    Форма для создания и редактирования категорий референсов
    """
    class Meta:
        model = ReferenceCategory
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название категории'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Описание категории (необязательно)'}),
        }

class ReferenceForm(forms.ModelForm):
    """
    Форма для создания и редактирования референсов
    """
    class Meta:
        model = Reference
        fields = ['title', 'category', 'image', 'description', 'source_url']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название референса'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Описание референса (необязательно)'}),
            'source_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com'}),
        }
    
    def clean_image(self):
        """
        Проверка размера изображения
        """
        image = self.cleaned_data.get('image')
        if image:
            if image.size > 10 * 1024 * 1024:  # 5 МБ
                raise forms.ValidationError(_('Размер изображения не должен превышать 5 МБ'))
        return image
    
    def clean_source_url(self):
        """
        Проверка формата URL источника
        """
        source_url = self.cleaned_data.get('source_url')
        if source_url:
            try:
                URLValidator()(source_url)
            except forms.ValidationError:
                if not source_url.startswith(('http://', 'https://')):
                    source_url = 'https://' + source_url
                    try:
                        URLValidator()(source_url)
                    except forms.ValidationError:
                        raise forms.ValidationError(_('Введите корректный URL'))
        return source_url

class ReferenceSearchForm(forms.Form):
    """
    Форма для поиска референсов
    """
    query = forms.CharField(
        label=_('Поиск'),
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Поиск референсов...'})
    )
    category = forms.ModelChoiceField(
        label=_('Категория'),
        queryset=ReferenceCategory.objects.none(),
        required=False,
        empty_label=_('Все категории'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = ReferenceCategory.objects.filter(photographer=user)

