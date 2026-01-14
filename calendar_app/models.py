from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from users.models import CustomUser
from clients.models import Client
from studios.models import Studio

class Event(models.Model):
    """
    Модель для хранения событий в календаре (съемки и посты)
    """
    EVENT_TYPE_CHOICES = [
        ('photoshoot', _('Фотосъемка')),
        ('post', _('Пост в соцсети')),
    ]
    
    photographer = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='events',
        verbose_name=_('фотограф')
    )
    title = models.CharField(_('название'), max_length=255)
    event_type = models.CharField(
        _('тип события'), 
        max_length=20, 
        choices=EVENT_TYPE_CHOICES, 
        default='photoshoot'
    )
    start_datetime = models.DateTimeField(_('дата и время начала'))
    end_datetime = models.DateTimeField(_('дата и время окончания'), blank=True, null=True)
    client = models.ForeignKey(
        Client, 
        on_delete=models.SET_NULL, 
        related_name='events',
        verbose_name=_('клиент'),
        null=True,
        blank=True
    )
    studio = models.ForeignKey(
        Studio, 
        on_delete=models.SET_NULL, 
        related_name='events',
        verbose_name=_('студия/локация'),
        null=True,
        blank=True
    )
    description = models.TextField(_('описание'), blank=True, max_length=500)
    is_all_day = models.BooleanField(_('весь день'), default=False)
    color = models.CharField(_('цвет'), max_length=20, default='#3788d8')
    created_at = models.DateTimeField(_('дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('дата обновления'), auto_now=True)
    
    class Meta:
        verbose_name = _('событие')
        verbose_name_plural = _('события')
        ordering = ['start_datetime']
        
    def __str__(self):
        return self.title
    
    @property
    def event_type_display(self):
        """Возвращает отображаемое значение типа события"""
        return dict(self.EVENT_TYPE_CHOICES).get(self.event_type, self.event_type)

    @staticmethod
    def get_type_event_by_str(type_event_str):
        for key, label in Event.EVENT_TYPE_CHOICES:
            print(key, label)
            if str(label) == type_event_str:
                return key
        return None


    @staticmethod
    def serialize_for_calendar(events):
        return [
            {
                'id': event.id,
                'title': event.title,
                'start': event.start_datetime.isoformat(),
                'end': event.end_datetime.isoformat() if event.end_datetime is not None else event.start_datetime.isoformat(),
                'allDay': event.is_all_day,
                'color': event.color,
                'url': reverse('calendar:event_detail', args=[event.id]),
                'extendedProps': {
                    'event_type': event.event_type,
                    'event_type_display': str(event.get_event_type_display()),
                    'description': event.description,
                    'client': event.client.get_full_name() if event.client else None,
                    'studio': event.studio.name if event.studio else None,
                }
            }
            for event in events
        ]



