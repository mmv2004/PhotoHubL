from django.urls import path
from django.contrib.auth.views import (
    LogoutView,
)
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='users:login'), name='logout'),
    path('profile/', views.ProfileUpdateView.as_view(), name='profile'),
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),

    # Новые URL для подтверждения email и восстановления пароля
    path('confirm-email/', views.confirm_email_view, name='confirm_email'),
    path('password-reset/', views.password_reset_request_view, name='password_reset_request'),
    path('password-reset/confirm/', views.password_reset_confirm_view, name='password_reset_confirm'),

    # Новый URL для переключения темы
    path('toggle-theme/', views.toggle_theme_view, name='toggle_theme'),

    path('', views.dashboard_view, name='dashboard'),
]