from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class RegisterViewTest(TestCase):
    def test_register_page_returns_200(self):
        response = self.client.get(reverse("accounts:register"))
        self.assertEqual(response.status_code, 200)

    def test_register_creates_user_and_redirects(self):
        response = self.client.post(reverse("accounts:register"), {
            "username": "newuser",
            "first_name": "Иван",
            "last_name": "Иванов",
            "email": "ivan@example.com",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
        })
        self.assertTrue(User.objects.filter(username="newuser").exists())
        self.assertEqual(response.status_code, 302)


class LoginViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="pass123")

    def test_login_page_returns_200(self):
        response = self.client.get(reverse("accounts:login"))
        self.assertEqual(response.status_code, 200)

    def test_login_with_valid_credentials(self):
        response = self.client.post(reverse("accounts:login"), {
            "username": "testuser",
            "password": "pass123",
        })
        self.assertEqual(response.status_code, 302)

    def test_login_with_invalid_credentials(self):
        response = self.client.post(reverse("accounts:login"), {
            "username": "testuser",
            "password": "wrongpass",
        })
        self.assertEqual(response.status_code, 200)


class LogoutViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="pass123")

    def test_logout_redirects(self):
        self.client.login(username="testuser", password="pass123")
        response = self.client.get(reverse("accounts:logout"))
        self.assertRedirects(response, reverse("products:product_list"))


class ProfileViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="pass123")

    def test_profile_requires_login(self):
        url = reverse("accounts:profile")
        response = self.client.get(url)
        self.assertRedirects(response, f"/accounts/login/?next={url}")

    def test_profile_returns_200_for_authenticated(self):
        self.client.login(username="testuser", password="pass123")
        response = self.client.get(reverse("accounts:profile"))
        self.assertEqual(response.status_code, 200)
