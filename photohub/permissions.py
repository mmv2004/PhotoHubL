from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from users.models import CustomUser
from clients.models import Client
from studios.models import Studio, StudioImage
from references.models import ReferenceCategory, Reference
from calendar_app.models import Event

def create_admin_group():
    """
    Создает группу администраторов с полными правами на все модели
    """
    admin_group, created = Group.objects.get_or_create(name='Администраторы')
    
    # Получаем все права для всех моделей
    all_permissions = Permission.objects.all()
    
    # Добавляем все права в группу администраторов
    admin_group.permissions.set(all_permissions)
    
    return admin_group

def create_photographer_group():
    """
    Создает группу фотографов с правами на управление своими данными
    """
    photographer_group, created = Group.objects.get_or_create(name='Фотографы')
    
    # Получаем типы контента для всех моделей
    user_ct = ContentType.objects.get_for_model(CustomUser)
    client_ct = ContentType.objects.get_for_model(Client)
    studio_ct = ContentType.objects.get_for_model(Studio)
    studio_image_ct = ContentType.objects.get_for_model(StudioImage)
    reference_category_ct = ContentType.objects.get_for_model(ReferenceCategory)
    reference_ct = ContentType.objects.get_for_model(Reference)
    event_ct = ContentType.objects.get_for_model(Event)
    
    # Получаем права для каждой модели
    user_permissions = Permission.objects.filter(
        Q(codename__startswith='view_') | Q(codename__startswith='change_'),
        content_type=user_ct
    )
    
    client_permissions = Permission.objects.filter(
        content_type=client_ct
    )
    
    studio_permissions = Permission.objects.filter(
        content_type=studio_ct
    )
    
    studio_image_permissions = Permission.objects.filter(
        content_type=studio_image_ct
    )
    
    reference_category_permissions = Permission.objects.filter(
        content_type=reference_category_ct
    )
    
    reference_permissions = Permission.objects.filter(
        content_type=reference_ct
    )
    
    event_permissions = Permission.objects.filter(
        content_type=event_ct
    )
    
    # Объединяем все права
    photographer_permissions = list(user_permissions) + \
                              list(client_permissions) + \
                              list(studio_permissions) + \
                              list(studio_image_permissions) + \
                              list(reference_category_permissions) + \
                              list(reference_permissions) + \
                              list(event_permissions)
    
    # Добавляем права в группу фотографов
    photographer_group.permissions.set(photographer_permissions)
    
    return photographer_group

def create_client_group():
    """
    Создает группу клиентов с ограниченными правами
    """
    client_group, created = Group.objects.get_or_create(name='Клиенты')
    
    # Получаем типы контента для всех моделей
    user_ct = ContentType.objects.get_for_model(CustomUser)
    client_ct = ContentType.objects.get_for_model(Client)
    studio_ct = ContentType.objects.get_for_model(Studio)
    reference_ct = ContentType.objects.get_for_model(Reference)
    event_ct = ContentType.objects.get_for_model(Event)
    
    # Получаем права для каждой модели (только просмотр)
    user_permissions = Permission.objects.filter(
        codename__startswith='view_',
        content_type=user_ct
    )
    
    client_permissions = Permission.objects.filter(
        Q(codename__startswith='view_') | Q(codename__startswith='change_'),
        content_type=client_ct
    )
    
    studio_permissions = Permission.objects.filter(
        codename__startswith='view_',
        content_type=studio_ct
    )
    
    reference_permissions = Permission.objects.filter(
        codename__startswith='view_',
        content_type=reference_ct
    )
    
    event_permissions = Permission.objects.filter(
        codename__startswith='view_',
        content_type=event_ct
    )
    
    # Объединяем все права
    client_permissions_list = list(user_permissions) + \
                             list(client_permissions) + \
                             list(studio_permissions) + \
                             list(reference_permissions) + \
                             list(event_permissions)
    
    # Добавляем права в группу клиентов
    client_group.permissions.set(client_permissions_list)
    
    return client_group

def setup_permissions():
    """
    Настраивает все группы и права доступа
    """
    admin_group = create_admin_group()
    photographer_group = create_photographer_group()
    client_group = create_client_group()
    
    # Добавляем суперпользователя в группу администраторов
    try:
        admin_user = CustomUser.objects.get(username='admin')
        admin_user.groups.add(admin_group)
    except CustomUser.DoesNotExist:
        pass
    
    # Добавляем всех пользователей с is_photographer=True в группу фотографов
    photographer_users = CustomUser.objects.filter(is_photographer=True)
    for user in photographer_users:
        user.groups.add(photographer_group)
    
    # Добавляем всех пользователей с is_photographer=False в группу клиентов
    client_users = CustomUser.objects.filter(is_photographer=False, is_staff=False, is_superuser=False)
    for user in client_users:
        user.groups.add(client_group)
    
    return {
        'admin_group': admin_group,
        'photographer_group': photographer_group,
        'client_group': client_group
    }

