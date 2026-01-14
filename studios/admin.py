from django.contrib import admin
from .models import Studio, StudioImage

class StudioImageInline(admin.TabularInline):
    model = StudioImage
    extra = 1
    fields = ('image', 'caption', 'is_main')

@admin.register(Studio)
class StudioAdmin(admin.ModelAdmin):
    list_display = ('name', 'location_type', 'city', 'full_address', 'is_public', 'created_by')
    list_filter = ('location_type', 'city', 'is_public')
    search_fields = ('name', 'city', 'district', 'full_address')
    inlines = [StudioImageInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'location_type', 'is_public', 'created_by')
        }),
        ('Адрес', {
            'fields': ('full_address', 'city', 'district', 'latitude', 'longitude')
        }),
        ('Дополнительная информация', {
            'fields': ('website', 'description')
        }),
    )

    def get_queryset(self, request):
        """
        Показывать все студии администраторам, а обычным пользователям - только публичные и созданные ими
        """
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(is_public=True) | qs.filter(created_by=request.user)

    def save_model(self, request, obj, form, change):
        """
        Автоматически устанавливаем текущего пользователя как создателя, если не указано иное
        """
        if not change and not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(StudioImage)
class StudioImageAdmin(admin.ModelAdmin):
    list_display = ('studio', 'caption', 'is_main', 'created_at')
    list_filter = ('is_main', 'created_at')
    search_fields = ('studio__name', 'caption')
    date_hierarchy = 'created_at'

