from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware
from datetime import datetime, timedelta

from .models import Event
from .forms import EventForm, EventFormPost
from clients.models import Client
from studios.models import Studio

from django.utils.safestring import mark_safe
import json

class CalendarView(LoginRequiredMixin, TemplateView):
    """
    Представление для отображения календаря
    """
    template_name = 'calendar_app/calendar.html'
    
    def get_context_data(self, **kwargs):
        """
        Добавляем дополнительные данные в контекст
        """
        context = super().get_context_data(**kwargs)


        event_filter = self.request.GET.get('filter')
        user = self.request.user

        if event_filter is None:
            events = Event.objects.filter(event_type='photoshoot', photographer=user)
        else:
            events = Event.objects.filter(event_type=event_filter, photographer=user)
        context['events'] = mark_safe(json.dumps(Event.serialize_for_calendar(events)))


        context['clients'] = Client.objects.filter(photographer=self.request.user)
        context['studios'] = Studio.objects.filter(is_public=True) | Studio.objects.filter(created_by=self.request.user)
        return context


class EventDetailView(LoginRequiredMixin, DetailView):
    """
    Представление для отображения деталей события
    """
    model = Event
    template_name = 'calendar_app/event_detail.html'
    context_object_name = 'event'
    
    def get_queryset(self):
        """
        Фильтрация событий по текущему пользователю
        """
        return Event.objects.filter(photographer=self.request.user)

class EventCreateView(LoginRequiredMixin, CreateView):
    """
    Представление для создания нового события
    """
    model = Event
    # form_class = EventForm
    template_name = 'calendar_app/event_form.html'
    
    # def get_form_kwargs(self):
    #     """
    #     Передаем текущего пользователя в форму
    #     """
    #     kwargs = super().get_form_kwargs()
    #     kwargs['user'] = self.request.user
    #     return kwargs
    #
    # def form_valid(self, form):
    #     """
    #     Устанавливаем текущего пользователя как фотографа
    #     """
    #     form.instance.photographer = self.request.user
    #     messages.success(self.request, 'Событие успешно создано!')
    #     return super().form_valid(form)
    #
    # def get_success_url(self):
    #     """
    #     Возвращаем URL для перенаправления после успешного создания
    #     """
    #     return reverse('calendar:event_detail', kwargs={'pk': self.object.pk})

    def get_form_class(self):
        form_type = self.request.GET.get('filter', "photoshoot")
        if form_type == 'photoshoot':
            return EventForm
        else:
            return EventFormPost

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form_type = self.request.GET.get('filter', "photoshoot")
        form.instance.event_type = form_type
        form.instance.photographer = self.request.user
        messages.success(self.request, 'Событие успешно создано!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('calendar:event_detail', kwargs={'pk': self.object.pk})

class EventUpdateView(LoginRequiredMixin, UpdateView):
    """
    Представление для редактирования события
    """
    model = Event
    form_class = EventForm
    template_name = 'calendar_app/event_form.html'
    
    def get_queryset(self):
        """
        Фильтрация событий по текущему пользователю
        """
        return Event.objects.filter(photographer=self.request.user)
    
    def get_form_kwargs(self):
        """
        Передаем текущего пользователя в форму
        """
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        """
        Добавляем сообщение об успешном обновлении
        """
        messages.success(self.request, 'Событие успешно обновлено!')
        return super().form_valid(form)
    
    def get_success_url(self):
        """
        Возвращаем URL для перенаправления после успешного обновления
        """
        return reverse('calendar:event_detail', kwargs={'pk': self.object.pk})

class EventDeleteView(LoginRequiredMixin, DeleteView):
    """
    Представление для удаления события
    """
    model = Event
    template_name = 'calendar_app/event_confirm_delete.html'
    success_url = reverse_lazy('calendar:calendar')
    
    def get_queryset(self):
        """
        Фильтрация событий по текущему пользователю
        """
        return Event.objects.filter(photographer=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        """
        Добавляем сообщение об успешном удалении
        """
        messages.success(self.request, 'Событие успешно удалено!')
        return super().delete(request, *args, **kwargs)

@login_required
def get_events_json(request):
    """
    Функция для получения событий в формате JSON для календаря
    """
    start = request.GET.get('start', None)
    end = request.GET.get('end', None)
    
    if start:
        start_date = make_aware(datetime.fromisoformat(start.replace('Z', '+00:00')))
    else:
        start_date = make_aware(datetime.now() - timedelta(days=30))
    
    if end:
        end_date = make_aware(datetime.fromisoformat(end.replace('Z', '+00:00')))
    else:
        end_date = make_aware(datetime.now() + timedelta(days=30))
    
    events = Event.objects.filter(
        photographer=request.user,
        start_datetime__gte=start_date,
        end_datetime__lte=end_date
    )
    
    event_list = []
    for event in events:
        event_dict = {
            'id': event.id,
            'title': event.title,
            'start': event.start_datetime.isoformat(),
            'end': event.end_datetime.isoformat(),
            'allDay': event.is_all_day,
            'color': event.color,
            'url': reverse('calendar:event_detail', args=[event.id]),
            'extendedProps': {
                'event_type': event.event_type,
                'event_type_display': event.event_type_display,
                'description': event.description,
                'client': event.client.get_full_name() if event.client else None,
                'studio': event.studio.name if event.studio else None,
            }
        }
        event_list.append(event_dict)
    
    return JsonResponse(event_list, safe=False)

@login_required
def get_filtered_events_json(request, event_type):
    """
    Функция для получения отфильтрованных событий в формате JSON для календаря
    """
    start = request.GET.get('start', None)
    end = request.GET.get('end', None)
    
    if start:
        start_date = make_aware(datetime.fromisoformat(start.replace('Z', '+00:00')))
    else:
        start_date = make_aware(datetime.now() - timedelta(days=30))
    
    if end:
        end_date = make_aware(datetime.fromisoformat(end.replace('Z', '+00:00')))
    else:
        end_date = make_aware(datetime.now() + timedelta(days=30))
    
    events = Event.objects.filter(
        photographer=request.user,
        start_datetime__gte=start_date,
        end_datetime__lte=end_date,
        event_type=event_type
    )
    
    event_list = []
    for event in events:
        event_dict = {
            'id': event.id,
            'title': event.title,
            'start': event.start_datetime.isoformat(),
            'end': event.end_datetime.isoformat(),
            'allDay': event.is_all_day,
            'color': event.color,
            'url': reverse('calendar:event_detail', args=[event.id]),
            'extendedProps': {
                'event_type': event.event_type,
                'event_type_display': event.event_type_display,
                'description': event.description,
                'client': event.client.get_full_name() if event.client else None,
                'studio': event.studio.name if event.studio else None,
            }
        }
        event_list.append(event_dict)
    
    return JsonResponse(event_list, safe=False)

