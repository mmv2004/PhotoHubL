from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import Client

User = get_user_model()

class ClientModelTest(TestCase):
    """
    Тесты для модели клиента
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
        self.client_model = Client.objects.create(
            photographer=self.user,
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            phone_number='+1234567890',
            address='123 Test St',
            notes='Test notes'
        )
    
    def test_client_creation(self):
        """
        Тест создания клиента
        """
        self.assertEqual(self.client_model.photographer, self.user)
        self.assertEqual(self.client_model.first_name, 'John')
        self.assertEqual(self.client_model.last_name, 'Doe')
        self.assertEqual(self.client_model.email, 'john@example.com')
        self.assertEqual(self.client_model.phone_number, '+1234567890')
        self.assertEqual(self.client_model.address, '123 Test St')
        self.assertEqual(self.client_model.notes, 'Test notes')
    
    def test_client_str(self):
        """
        Тест строкового представления клиента
        """
        self.assertEqual(str(self.client_model), 'John Doe')
    
    def test_get_full_name(self):
        """
        Тест получения полного имени клиента
        """
        self.assertEqual(self.client_model.get_full_name(), 'John Doe')

class ClientViewsTest(TestCase):
    """
    Тесты для представлений клиента
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
        self.client_model = Client.objects.create(
            photographer=self.user,
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            phone_number='+1234567890',
            address='123 Test St',
            notes='Test notes'
        )
        self.client_list_url = reverse('clients:client_list')
        self.client_detail_url = reverse('clients:client_detail', args=[self.client_model.id])
        self.client_create_url = reverse('clients:client_create')
        self.client_update_url = reverse('clients:client_update', args=[self.client_model.id])
        self.client_delete_url = reverse('clients:client_delete', args=[self.client_model.id])
        self.login_url = reverse('users:login')
    
    def test_client_list_view_authenticated(self):
        """
        Тест доступа к списку клиентов для аутентифицированного пользователя
        """
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.client_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clients/client_list.html')
        self.assertContains(response, 'John Doe')
    
    def test_client_list_view_unauthenticated(self):
        """
        Тест доступа к списку клиентов для неаутентифицированного пользователя
        """
        response = self.client.get(self.client_list_url)
        self.assertRedirects(response, f'{self.login_url}?next={self.client_list_url}')
    
    def test_client_detail_view_authenticated(self):
        """
        Тест доступа к деталям клиента для аутентифицированного пользователя
        """
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.client_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clients/client_detail.html')
        self.assertContains(response, 'John Doe')
        self.assertContains(response, 'john@example.com')
    
    def test_client_detail_view_unauthenticated(self):
        """
        Тест доступа к деталям клиента для неаутентифицированного пользователя
        """
        response = self.client.get(self.client_detail_url)
        self.assertRedirects(response, f'{self.login_url}?next={self.client_detail_url}')
    
    def test_client_create_view_authenticated(self):
        """
        Тест доступа к созданию клиента для аутентифицированного пользователя
        """
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.client_create_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clients/client_form.html')
    
    def test_client_create_view_post_valid(self):
        """
        Тест POST-запроса к созданию клиента с валидными данными
        """
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(self.client_create_url, {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane@example.com',
            'phone_number': '+0987654321',
            'address': '456 Test Ave',
            'notes': 'New client'
        })
        self.assertRedirects(response, self.client_list_url)
        self.assertTrue(Client.objects.filter(email='jane@example.com').exists())
    
    def test_client_update_view_authenticated(self):
        """
        Тест доступа к обновлению клиента для аутентифицированного пользователя
        """
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.client_update_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clients/client_form.html')
        self.assertContains(response, 'John Doe')
    
    def test_client_update_view_post_valid(self):
        """
        Тест POST-запроса к обновлению клиента с валидными данными
        """
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(self.client_update_url, {
            'first_name': 'John',
            'last_name': 'Smith',
            'email': 'john@example.com',
            'phone_number': '+1234567890',
            'address': '123 Test St',
            'notes': 'Updated notes'
        })
        self.assertRedirects(response, self.client_detail_url)
        self.client_model.refresh_from_db()
        self.assertEqual(self.client_model.last_name, 'Smith')
        self.assertEqual(self.client_model.notes, 'Updated notes')
    
    def test_client_delete_view_authenticated(self):
        """
        Тест доступа к удалению клиента для аутентифицированного пользователя
        """
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.client_delete_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clients/client_confirm_delete.html')
    
    def test_client_delete_view_post(self):
        """
        Тест POST-запроса к удалению клиента
        """
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(self.client_delete_url)
        self.assertRedirects(response, self.client_list_url)
        self.assertFalse(Client.objects.filter(id=self.client_model.id).exists())

