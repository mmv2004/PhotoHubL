from django.contrib import admin
from .models import Client

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone_number', 'photographer', 'created_at')
    list_filter = ('created_at', 'photographer')
    search_fields = ('first_name', 'last_name', 'email', 'phone_number')
    date_hierarchy = 'created_at'
    fieldsets = (
        (None, {
            'fields': ('photographer', 'first_name', 'last_name')
        }),
        ('Контактная информация', {
            'fields': ('email', 'phone_number', 'address')
        }),
        ('Дополнительная информация', {
            'fields': ('birth_date', 'notes')
        }),
    )
    
    def get_queryset(self, request):
        """
        Фильтрация клиентов по текущему пользователю, если он не администратор
        """
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(photographer=request.user)

