from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserChangeForm

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_staff', 'is_photographer')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'is_photographer')
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        (_('Персональная информация'), {'fields': ('first_name', 'last_name', 'birth_date', 'avatar', 'phone_number')}),
        (_('Права доступа'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_photographer', 'groups', 'user_permissions')}),
        (_('Важные даты'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'first_name', 'last_name', 'password1', 'password2', 'is_photographer'),
        }),
    )
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('email',)

