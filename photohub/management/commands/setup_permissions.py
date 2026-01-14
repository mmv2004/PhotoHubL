from django.core.management.base import BaseCommand
from photohub.permissions import setup_permissions

class Command(BaseCommand):
    help = 'Настройка групп и прав доступа для пользователей'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Начинаем настройку прав доступа...'))
        
        result = setup_permissions()
        
        self.stdout.write(self.style.SUCCESS(f'Группа "{result["admin_group"].name}" настроена'))
        self.stdout.write(self.style.SUCCESS(f'Группа "{result["photographer_group"].name}" настроена'))
        self.stdout.write(self.style.SUCCESS(f'Группа "{result["client_group"].name}" настроена'))
        
        self.stdout.write(self.style.SUCCESS('Настройка прав доступа завершена успешно!'))

