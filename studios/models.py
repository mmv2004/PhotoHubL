from django.db import models
from django.utils.translation import gettext_lazy as _
from users.models import CustomUser

class Studio(models.Model):
    """
    Модель для хранения информации о фотостудиях и местах для съемок
    """
    LOCATION_TYPE_CHOICES = [
        ('studio', _('Студия')),
        ('outdoor', _('Улица')),
    ]

    name = models.CharField(_('название'), max_length=50)
    location_type = models.CharField(
        _('тип локации'),
        max_length=10,
        choices=LOCATION_TYPE_CHOICES,
        default='studio'
    )
    city = models.CharField(_('город'), max_length=50)
    district = models.CharField(_('район'), max_length=50, blank=True)
    full_address = models.CharField(_('полный адрес'), max_length=255, blank=True)
    website = models.URLField(_('веб-сайт'), blank=True)
    description = models.TextField(_('описание'), blank=True, max_length=500)
    latitude = models.FloatField(_('широта'), null=True, blank=True, help_text=_('Координаты определяются автоматически по адресу'))
    longitude = models.FloatField(_('долгота'), null=True, blank=True, help_text=_('Координаты определяются автоматически по адресу'))
    is_public = models.BooleanField(_('публичная'), default=False, help_text=_('Если отмечено, студия будет видна всем пользователям'))
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='created_studios',
        verbose_name=_('создатель')
    )
    created_at = models.DateTimeField(_('дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('дата обновления'), auto_now=True)

    class Meta:
        verbose_name = _('студия/локация')
        verbose_name_plural = _('студии/локации')
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_full_address(self):
        """Возвращает полный адрес студии/локации"""
        return self.full_address or f"{self.city}, {self.district}"

class StudioImage(models.Model):
    """
    Модель для хранения изображений фотостудий и мест для съемок
    """
    studio = models.ForeignKey(
        Studio,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_('студия/локация')
    )
    image = models.ImageField(_('изображение'), upload_to='studios/')
    caption = models.CharField(_('подпись'), max_length=255, blank=True)
    is_main = models.BooleanField(_('главное изображение'), default=False)
    created_at = models.DateTimeField(_('дата создания'), auto_now_add=True)

    class Meta:
        verbose_name = _('изображение студии')
        verbose_name_plural = _('изображения студий')
        ordering = ['-is_main', 'created_at']

    def __str__(self):
        return f"{self.studio.name} - {self.caption if self.caption else 'Изображение'}"

    def save(self, *args, **kwargs):
        """Если изображение отмечено как главное, снимаем этот флаг с других изображений студии"""
        if self.is_main:
            StudioImage.objects.filter(studio=self.studio, is_main=True).update(is_main=False)
        super().save(*args, **kwargs)

