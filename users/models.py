from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator


class CustomUser(AbstractUser):
    """
    Расширенная модель пользователя с дополнительными полями
    """
    first_name = models.CharField(_('имя'), max_length=150)
    last_name = models.CharField(_('фамилия'), max_length=150)
    email = models.EmailField(_('email адрес'), unique=True)
    birth_date = models.DateField(_('дата рождения'), null=True, blank=True)
    avatar = models.ImageField(_('аватар'), upload_to='avatars/', null=True, blank=True)
    phone_regex = RegexValidator(
        regex=r'^\+?7?\d{10}$',
        message="Введите номер телефона в формате: '+72345678901' — '+7' и ровно 10 цифр."
    )
    phone_number = models.CharField(_('номер телефона'), validators=[phone_regex], blank=True)
    is_photographer = models.BooleanField(_('фотограф'), default=True)

    # Новые поля для подтверждения email и восстановления пароля
    email_confirmed = models.BooleanField(_('email подтвержден'), default=False)
    confirmation_code = models.CharField(_('код подтверждения'), max_length=6, blank=True, null=True)
    confirmation_code_created = models.DateTimeField(_('время создания кода'), auto_now_add=True)

    # Новое поле для темной темы
    dark_theme = models.BooleanField(_('темная тема'), default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = _('пользователь')
        verbose_name_plural = _('пользователи')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"