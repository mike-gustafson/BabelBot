# translator/tests.py
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

class AuthenticationTests(TestCase):
    def test_register_user(self):
        # Test successful registration
        response = self.client.post(reverse('register'), {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful registration
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_register_user_password_mismatch(self):
        # Test registration with mismatched passwords
        response = self.client.post(reverse('register'), {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'password123',
            'confirm_password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after error
        self.assertFalse(User.objects.filter(username='testuser').exists())

    def test_login_user(self):
        # Test successful login
        User.objects.create_user(username='testuser', email='testuser@example.com', password='password123')
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful login
        self.assertIn('_auth_user_id', self.client.session)

    def test_login_invalid_credentials(self):
        # Test login with invalid credentials
        response = self.client.post(reverse('login'), {
            'username': 'nonexistentuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after failed login
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_logout_user(self):
        # Test successful logout
        user = User.objects.create_user(username='testuser', email='testuser@example.com', password='password123')
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Redirect after logout
        self.assertNotIn('_auth_user_id', self.client.session)