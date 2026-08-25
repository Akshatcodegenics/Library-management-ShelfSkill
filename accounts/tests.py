from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


class AccountsAuthTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_user_signup_creates_normal_user(self):
        response = self.client.post('/api/auth/signup/', {
            'username': 'normal_user',
            'email': 'normal@test.com',
            'password': 'password123',
            'name': 'Normal User',
            'phone': '1234567890'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['user']['role'], 'USER')
        
        user = User.objects.get(email='normal@test.com')
        self.assertEqual(user.role, 'USER')
        self.assertFalse(user.is_staff)

    def test_admin_register_with_correct_secret_key(self):
        response = self.client.post('/api/auth/admin/register/', {
            'username': 'admin_user',
            'email': 'admin@test.com',
            'password': 'password123',
            'name': 'System Admin',
            'admin_secret_key': 'library-admin-secret-2026'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['user']['role'], 'ADMIN')

        user = User.objects.get(email='admin@test.com')
        self.assertEqual(user.role, 'ADMIN')
        self.assertTrue(user.is_staff)

    def test_admin_register_with_invalid_secret_key_rejected(self):
        response = self.client.post('/api/auth/admin/register/', {
            'username': 'fake_admin',
            'email': 'fake@test.com',
            'password': 'password123',
            'name': 'Fake Admin',
            'admin_secret_key': 'WRONG_SECRET_KEY'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
