from django.db import models
from django.utils.translation import gettext_lazy as _
from users.models import CustomUser

class ReferenceCategory(models.Model):
    """
    Модель для категорий референсов
    """
    photographer = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='reference_categories',
        verbose_name=_('фотограф')
    )
    name = models.CharField(_('название'), max_length=50)
    description = models.TextField(_('описание'), blank=True, max_length=500)
    created_at = models.DateTimeField(_('дата создания'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('категория референсов')
        verbose_name_plural = _('категории референсов')
        ordering = ['name']
        
    def __str__(self):
        return self.name

class Reference(models.Model):
    """
    Модель для хранения референсов (изображений для вдохновения)
    """
    photographer = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='references',
        verbose_name=_('фотограф')
    )
    category = models.ForeignKey(
        ReferenceCategory, 
        on_delete=models.SET_NULL, 
        related_name='references',
        verbose_name=_('категория'),
        null=True,
        blank=True
    )
    title = models.CharField(_('название'), max_length=50)
    image = models.ImageField(_('изображение'), upload_to='references/')
    description = models.TextField(_('описание'), blank=True, max_length=500)
    source_url = models.URLField(_('источник'), blank=True, max_length=500)
    created_at = models.DateTimeField(_('дата создания'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('референс')
        verbose_name_plural = _('референсы')
        ordering = ['-created_at']
        
    def __str__(self):
        return self.title

