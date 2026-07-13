from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import Client, TestCase
from django.urls import reverse

from apps.leads.tests.factories import create_user


User = get_user_model()


class SignupTests(TestCase):
    def test_signup_get_renders_form(self):
        response = self.client.get(reverse("leads:signup"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/signup.html")

    def test_valid_signup_creates_user_and_redirects_to_login(self):
        response = self.client.post(
            reverse("leads:signup"),
            {
                "username": "newuser",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )
        self.assertRedirects(response, reverse("login"))
        user = User.objects.get(username="newuser")
        self.assertTrue(user.check_password("StrongPass123!"))

    def test_duplicate_username_does_not_create_user(self):
        create_user(username="dupe")
        response = self.client.post(
            reverse("leads:signup"),
            {"username": "dupe", "password1": "StrongPass123!", "password2": "StrongPass123!"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(username="dupe").count(), 1)

    def test_weak_password_is_rejected(self):
        response = self.client.post(
            reverse("leads:signup"),
            {"username": "weak", "password1": "123", "password2": "123"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="weak").exists())

    def test_mismatched_passwords_are_rejected(self):
        response = self.client.post(
            reverse("leads:signup"),
            {"username": "mismatch", "password1": "StrongPass123!", "password2": "OtherPass123!"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="mismatch").exists())

    def test_missing_fields_are_rejected(self):
        response = self.client.post(reverse("leads:signup"), {})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 0)

    def test_authenticated_user_can_access_signup_current_behavior(self):
        user = create_user(username="logged")
        self.client.force_login(user)
        response = self.client.get(reverse("leads:signup"))
        self.assertEqual(response.status_code, 200)


class LoginLogoutTests(TestCase):
    def setUp(self):
        self.user = create_user(username="loginuser", password="StrongPass123!")

    def test_login_get_renders_form(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/login.html")

    def test_valid_login_redirects_to_dashboard(self):
        response = self.client.post(
            reverse("login"),
            {"username": "loginuser", "password": "StrongPass123!"},
        )
        self.assertRedirects(response, reverse("leads:dashboard"))

    def test_wrong_password_keeps_user_on_login_page(self):
        response = self.client.post(
            reverse("login"),
            {"username": "loginuser", "password": "wrong"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Usu")

    def test_unknown_user_keeps_user_on_login_page(self):
        response = self.client.post(reverse("login"), {"username": "ghost", "password": "whatever"})
        self.assertEqual(response.status_code, 200)

    def test_empty_login_fields_are_rejected(self):
        response = self.client.post(reverse("login"), {"username": "", "password": ""})
        self.assertEqual(response.status_code, 200)

    def test_protected_route_redirects_anonymous_user_to_login(self):
        response = self.client.get(reverse("leads:dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_internal_next_parameter_is_honored(self):
        response = self.client.post(
            f"{reverse('login')}?next={reverse('leads:lead_list')}",
            {"username": "loginuser", "password": "StrongPass123!"},
        )
        self.assertRedirects(response, reverse("leads:lead_list"))

    def test_external_next_parameter_is_rejected_by_login_view(self):
        response = self.client.post(
            f"{reverse('login')}?next=https://evil.example/",
            {"username": "loginuser", "password": "StrongPass123!"},
        )
        self.assertRedirects(response, reverse("leads:dashboard"))

    def test_authenticated_user_gets_login_page_current_behavior(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)

    def test_logout_post_ends_session_and_redirects(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("login"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logout_post_without_authentication_redirects(self):
        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("login"))

    def test_logout_get_is_not_allowed_current_behavior(self):
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 405)


class CsrfAuthenticationTests(TestCase):
    def setUp(self):
        self.user = create_user(username="csrfuser", password="StrongPass123!")
        self.client = Client(enforce_csrf_checks=True)

    def test_login_post_without_csrf_is_forbidden(self):
        response = self.client.post(reverse("login"), {"username": "csrfuser", "password": "StrongPass123!"})
        self.assertEqual(response.status_code, 403)

    def test_login_post_with_csrf_succeeds(self):
        self.client.get(reverse("login"))
        token = self.client.cookies["csrftoken"].value
        response = self.client.post(
            reverse("login"),
            {"username": "csrfuser", "password": "StrongPass123!"},
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, 302)

    def test_logout_without_csrf_is_forbidden(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("logout"))
        self.assertEqual(response.status_code, 403)
