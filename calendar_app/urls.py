from django.urls import path
from . import views

app_name = 'calendar'

urlpatterns = [
    path('', views.CalendarView.as_view(), name='calendar'),
    path('events/add/', views.EventCreateView.as_view(), name='event_add'),
    path('events/<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),
    path('events/<int:pk>/edit/', views.EventUpdateView.as_view(), name='event_edit'),
    path('events/<int:pk>/delete/', views.EventDeleteView.as_view(), name='event_delete'),
    path('api/events/', views.get_events_json, name='events_json'),
    path('api/events/filter/<str:event_type>/', views.get_filtered_events_json, name='filtered_events_json'),
]

