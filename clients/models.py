from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from users.models import CustomUser


class Client(models.Model):
    """
    Модель для хранения информации о клиентах фотографа
    """
    photographer = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='clients',
        verbose_name=_('фотограф')
    )
    first_name = models.CharField(_('имя'), max_length=30)
    last_name = models.CharField(_('фамилия'), max_length=30)
    email = models.EmailField(_('email адрес'), blank=True)
    birth_date = models.DateField(_('дата рождения'), null=True, blank=True)
    phone_regex = RegexValidator(
        regex=r'^\+?7?\d{10}$',
        message="Введите номер телефона в формате: '+72345678901' — '+7' и ровно 10 цифр."
    )
    phone_number = models.CharField(_('номер телефона'), validators=[phone_regex], blank=True)
    address = models.CharField(_('адрес'), max_length=255, blank=True)
    notes = models.TextField(_('примечания'), blank=True, max_length=500)
    created_at = models.DateTimeField(_('дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('дата обновления'), auto_now=True)
    
    class Meta:
        verbose_name = _('клиент')
        verbose_name_plural = _('клиенты')
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

