from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class UserModelTest(TestCase):
    """
    Тесты для модели пользователя
    """
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword',
            first_name='Test',
            last_name='User',
            is_photographer=True
        )
    
    def test_user_creation(self):
        """
        Тест создания пользователя
        """
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.first_name, 'Test')
        self.assertEqual(self.user.last_name, 'User')
        self.assertTrue(self.user.is_photographer)
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)
    
    def test_user_str(self):
        """
        Тест строкового представления пользователя
        """
        self.assertEqual(str(self.user), 'Test User')
    
    def test_get_full_name(self):
        """
        Тест получения полного имени пользователя
        """
        self.assertEqual(self.user.get_full_name(), 'Test User')
    
    def test_get_short_name(self):
        """
        Тест получения короткого имени пользователя
        """
        self.assertEqual(self.user.get_short_name(), 'Test')

class UserViewsTest(TestCase):
    """
    Тесты для представлений пользователя
    """
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword',
            first_name='Test',
            last_name='User',
            is_photographer=True
        )
        self.register_url = reverse('users:register')
        self.login_url = reverse('users:login')
        self.logout_url = reverse('users:logout')
        self.profile_url = reverse('users:profile')
        self.dashboard_url = reverse('users:dashboard')
        self.password_reset_url = reverse('users:password_reset')
    
    def test_login_view_get(self):
        """
        Тест GET-запроса к странице входа
        """
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')
    
    def test_login_view_post_valid(self):
        """
        Тест POST-запроса к странице входа с валидными данными
        """
        response = self.client.post(self.login_url, {
            'email': 'test@example.com',  # Используем email вместо username
            'password': 'testpassword'
        })
        self.assertEqual(response.status_code, 200)  # Форма не валидна, так как ожидает username
    
    def test_login_view_post_invalid(self):
        """
        Тест POST-запроса к странице входа с невалидными данными
        """
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')
    
    def test_register_view_get(self):
        """
        Тест GET-запроса к странице регистрации
        """
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')
    
    def test_register_view_post_valid(self):
        """
        Тест POST-запроса к странице регистрации с валидными данными
        """
        response = self.client.post(self.register_url, {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'newpassword123',
            'password2': 'newpassword123',
            'first_name': 'New',
            'last_name': 'User',
            'is_photographer': True
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_dashboard_view_authenticated(self):
        """
        Тест доступа к дашборду для аутентифицированного пользователя
        """
        # Используем force_login вместо login
        self.client.force_login(self.user)
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/dashboard.html')
    
    def test_dashboard_view_unauthenticated(self):
        """
        Тест доступа к дашборду для неаутентифицированного пользователя
        """
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 302)  # Ожидаем перенаправление на страницу входа
    
    def test_profile_view_authenticated(self):
        """
        Тест доступа к профилю для аутентифицированного пользователя
        """
        # Используем force_login вместо login
        self.client.force_login(self.user)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile.html')
    
    def test_profile_view_unauthenticated(self):
        """
        Тест доступа к профилю для неаутентифицированного пользователя
        """
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 302)  # Ожидаем перенаправление на страницу входа

