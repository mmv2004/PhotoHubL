from django.contrib import admin
from .models import Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_type', 'start_datetime', 'end_datetime', 'client', 'photographer')
    list_filter = ('event_type', 'start_datetime', 'is_all_day', 'photographer')
    search_fields = ('title', 'description')
    date_hierarchy = 'start_datetime'
    fieldsets = (
        (None, {
            'fields': ('photographer', 'title', 'event_type', 'description')
        }),
        ('Время', {
            'fields': ('start_datetime', 'end_datetime', 'is_all_day')
        }),
        ('Связи', {
            'fields': ('client', 'studio')
        }),
        ('Оформление', {
            'fields': ('color',)
        }),
    )
    
    def get_queryset(self, request):
        """
        Фильтрация событий по текущему пользователю, если он не администратор
        """
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(photographer=request.user)
    
    def save_model(self, request, obj, form, change):
        """
        Автоматически устанавливаем текущего пользователя как фотографа, если не указано иное
        """
        if not change and not obj.photographer:
            obj.photographer = request.user
        super().save_model(request, obj, form, change)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Фильтрация клиентов и студий по текущему пользователю
        """
        if db_field.name == "client" and not request.user.is_superuser:
            kwargs["queryset"] = request.user.clients.all()
        if db_field.name == "studio" and not request.user.is_superuser:
            # Показываем публичные студии и студии, созданные пользователем
            from studios.models import Studio
            kwargs["queryset"] = Studio.objects.filter(is_public=True) | Studio.objects.filter(created_by=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

