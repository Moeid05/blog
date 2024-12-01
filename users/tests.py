from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.contrib.auth.models import Permission, Group
import logging

User  = get_user_model()

class CustomUser_Tests(TestCase):

    def setUp(self):
        self.username = 'testuser'
        self.email = 'testuser@example.com'
        self.password = 'testpassword123'
        self.user = User.objects.create_user(username=self.username, email=self.email, password=self.password)

    def test_user_registration(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpassword123',
            'password_confirm': 'newpassword123',  
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_user_login(self):
        response = self.client.post(reverse('login'), {
            'username': self.username,
            'password': self.password,
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.wsgi_request.user, self.user)

    def test_user_login_invalid(self):
        response = self.client.post(reverse('login'), {
            'username': self.username,
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', None, 'username/password is wrong')

    def test_user_logout(self):
        self.client.login(username=self.username, password=self.password)  # Log in the user
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_user_profile(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('profile', args=[self.username]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.username)

    def test_user_profile_not_authenticated(self):
        response = self.client.get(reverse('profile', args=[self.username]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('profile', args=[self.username])}")

    def test_user_following(self):
        other_user = User.objects.create_user(username='otheruser', email='otheruser@example.com', password='password123')
        self.user.following.add(other_user)
        self.assertIn(other_user, self.user.following.all())
        self.assertIn(self.user, other_user.followers.all())