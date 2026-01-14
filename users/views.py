import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse

from studios.models import Studio

from .forms import (
    CustomUserCreationForm,
    CustomUserChangeForm,
    CustomAuthenticationForm,
    EmailConfirmationForm,
    PasswordResetRequestForm,
    PasswordResetConfirmForm
)
from .models import CustomUser


# Функция для проверки, является ли пользователь администратором
def is_admin(user):
    return user.is_staff or user.is_superuser


def generate_confirmation_code():
    """Генерирует 6-значный код подтверждения."""
    return str(random.randint(100000, 999999))


def send_confirmation_email(user, code):
    """Отправляет Email с кодом подтверждения."""
    subject = 'Подтверждение регистрации на PhotoHub'
    message = f"""Здравствуйте, {user.first_name}!

Спасибо за регистрацию на PhotoHub.
Для завершения регистрации, пожалуйста, используйте следующий код подтверждения:

{code}

Если вы не регистрировались на нашем сайте, просто проигнорируйте это письмо.

С уважением,
Команда PhotoHub
"""
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )


def send_password_reset_email(user, code):
    """Отправляет Email с кодом для восстановления пароля."""
    subject = 'Восстановление пароля на PhotoHub'
    message = f"""Здравствуйте, {user.first_name}!

Вы запросили восстановление пароля на PhotoHub.
Для сброса пароля, пожалуйста, используйте следующий код:

{code}

Если вы не запрашивали сброс пароля, немедленно свяжитесь с нашей службой поддержки.

С уважением,
Команда PhotoHub
"""
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )


class RegisterView(CreateView):
    """
    Представление для регистрации нового пользователя
    """
    form_class = CustomUserCreationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:confirm_email')

    def form_valid(self, form):
        # Сохраняем пользователя
        user = form.save(commit=False)

        # Генерируем и сохраняем код подтверждения
        confirmation_code = generate_confirmation_code()
        user.confirmation_code = confirmation_code
        user.confirmation_code_created = timezone.now()
        user.email_confirmed = False
        user.save()

        # Отправляем email с кодом подтверждения
        send_confirmation_email(user, confirmation_code)

        # Авторизуем пользователя, но ограничиваем доступ пока email не подтвержден
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password1')
        user = authenticate(email=email, password=password)
        login(self.request, user)

        messages.success(self.request, 'Регистрация успешно завершена! Проверьте ваш email для подтверждения.')
        return redirect('users:confirm_email')

    def dispatch(self, request, *args, **kwargs):
        # Если пользователь уже авторизован, перенаправляем на дашборд
        if request.user.is_authenticated:
            return redirect('users:dashboard')
        return super().dispatch(request, *args, **kwargs)


class CustomLoginView(LoginView):
    """
    Представление для авторизации пользователя
    """
    form_class = CustomAuthenticationForm
    template_name = 'users/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        # Проверяем, подтвержден ли email
        user = form.get_user()
        if not user.email_confirmed:
            messages.error(self.request,
                           'Ваш email не подтвержден. Пожалуйста, подтвердите email для входа в систему.')
            return redirect('users:confirm_email')

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('users:dashboard')


@require_http_methods(["GET", "POST"])
def confirm_email_view(request):
    """
    Представление для подтверждения email
    """
    if not request.user.is_authenticated:
        messages.error(request, 'Для подтверждения email необходимо войти в систему.')
        return redirect('users:login')

    if request.user.email_confirmed:
        messages.info(request, 'Ваш email уже подтвержден.')
        return redirect('users:dashboard')

    if request.method == 'POST':
        form = EmailConfirmationForm(request.POST)
        if form.is_valid():
            confirmation_code = form.cleaned_data['confirmation_code']

            # Проверяем код подтверждения
            if (request.user.confirmation_code == confirmation_code and
                    request.user.confirmation_code_created and
                    timezone.now() - request.user.confirmation_code_created < timedelta(hours=24)):

                # Подтверждаем email
                request.user.email_confirmed = True
                request.user.confirmation_code = None
                request.user.save()

                messages.success(request, 'Ваш email успешно подтвержден!')
                return redirect('users:dashboard')
            else:
                messages.error(request, 'Неверный или устаревший код подтверждения.')
    else:
        form = EmailConfirmationForm()

        # Если пользователь зашел на страницу, можно отправить код повторно
        if not request.user.confirmation_code or (
                request.user.confirmation_code_created and
                timezone.now() - request.user.confirmation_code_created > timedelta(minutes=5)
        ):
            # Генерируем новый код
            new_code = generate_confirmation_code()
            request.user.confirmation_code = new_code
            request.user.confirmation_code_created = timezone.now()
            request.user.save()
            send_confirmation_email(request.user, new_code)
            messages.info(request, 'Код подтверждения отправлен на ваш email.')

    return render(request, 'users/confirm_email.html', {'form': form})


@require_http_methods(["GET", "POST"])
def password_reset_request_view(request):
    """
    Представление для запроса сброса пароля
    """
    if request.user.is_authenticated:
        return redirect('users:dashboard')

    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = CustomUser.objects.get(email=email)
                # Генерируем и сохраняем код подтверждения
                confirmation_code = generate_confirmation_code()
                user.confirmation_code = confirmation_code
                user.confirmation_code_created = timezone.now()
                user.save()

                # Отправляем email с кодом подтверждения
                send_password_reset_email(user, confirmation_code)

                messages.success(request, 'Код для восстановления пароля отправлен на ваш email.')
                # Сохраняем email в сессии для следующего шага
                request.session['password_reset_email'] = email
                return redirect('users:password_reset_confirm')

            except CustomUser.DoesNotExist:
                # Для безопасности не сообщаем, что пользователь не найден
                messages.success(request, 'Если email зарегистрирован, код будет отправлен.')
                return redirect('users:login')
    else:
        form = PasswordResetRequestForm()

    return render(request, 'users/password_reset_request.html', {'form': form})


@require_http_methods(["GET", "POST"])
def password_reset_confirm_view(request):
    """
    Представление для подтверждения сброса пароля и установки нового пароля
    """
    if request.user.is_authenticated:
        return redirect('users:dashboard')

    email = request.session.get('password_reset_email')
    if not email:
        messages.error(request, 'Сессия истекла. Пожалуйста, запросите сброс пароля снова.')
        return redirect('users:password_reset_request')

    try:
        user = CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        messages.error(request, 'Пользователь не найден.')
        return redirect('users:password_reset_request')

    if request.method == 'POST':
        form = PasswordResetConfirmForm(request.POST)
        if form.is_valid():
            confirmation_code = form.cleaned_data['confirmation_code']
            new_password = form.cleaned_data['new_password1']

            # Проверяем код подтверждения
            if (user.confirmation_code == confirmation_code and
                    user.confirmation_code_created and
                    timezone.now() - user.confirmation_code_created < timedelta(hours=24)):

                # Устанавливаем новый пароль
                user.set_password(new_password)
                user.confirmation_code = None
                user.save()

                # Очищаем сессию
                if 'password_reset_email' in request.session:
                    del request.session['password_reset_email']

                messages.success(request, 'Пароль успешно изменен! Теперь вы можете войти с новым паролем.')
                return redirect('users:login')
            else:
                messages.error(request, 'Неверный или устаревший код подтверждения.')
    else:
        form = PasswordResetConfirmForm()

    return render(request, 'users/password_reset_confirm.html', {
        'form': form,
        'email': email
    })


@login_required
@require_http_methods(["POST"])
def toggle_theme_view(request):
    """
    Представление для переключения темы
    """
    user = request.user
    user.dark_theme = not user.dark_theme
    user.save()

    # Принудительно обновляем сессию пользователя
    from django.contrib.auth import update_session_auth_hash
    update_session_auth_hash(request, user)

    # Редирект на ту же страницу
    return redirect(request.META.get('HTTP_REFERER', 'users:dashboard'))


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """
    Представление для редактирования профиля пользователя
    """
    model = CustomUser
    form_class = CustomUserChangeForm
    template_name = 'users/profile.html'
    success_url = reverse_lazy('users:profile')
    login_url = reverse_lazy('users:login')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Профиль успешно обновлен!')
        return super().form_valid(form)


@login_required(login_url='users:login')
def dashboard_view(request):
    return redirect(to="calendar:calendar")


# Представление для администраторов
@user_passes_test(is_admin, login_url='users:login')
def admin_dashboard_view(request):
    """
    Представление для административной панели
    """
    # Получаем всех пользователей
    users = CustomUser.objects.all().order_by('-date_joined')[:10]

    # Получаем все студии
    from studios.models import Studio
    studios = Studio.objects.all().order_by('-created_at')[:10]

    context = {
        'users': users,
        'studios': studios,
    }

    return render(request, 'users/admin_dashboard.html', context)