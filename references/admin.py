from django.contrib import admin
from .models import ReferenceCategory, Reference

@admin.register(ReferenceCategory)
class ReferenceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'photographer', 'created_at')
    list_filter = ('created_at', 'photographer')
    search_fields = ('name', 'description')
    date_hierarchy = 'created_at'
    
    def get_queryset(self, request):
        """
        Фильтрация категорий по текущему пользователю, если он не администратор
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

@admin.register(Reference)
class ReferenceAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'photographer', 'created_at')
    list_filter = ('category', 'created_at', 'photographer')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        """
        Предварительный просмотр изображения в админке
        """
        if obj.image:
            return f'<img src="{obj.image.url}" style="max-height: 200px; max-width: 200px;" />'
        return 'Нет изображения'
    
    image_preview.short_description = 'Предпросмотр'
    image_preview.allow_tags = True
    
    def get_queryset(self, request):
        """
        Фильтрация референсов по текущему пользователю, если он не администратор
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
        Фильтрация категорий по текущему пользователю
        """
        if db_field.name == "category" and not request.user.is_superuser:
            kwargs["queryset"] = ReferenceCategory.objects.filter(photographer=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

