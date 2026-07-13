from django.test import TestCase
from django.urls import reverse

from leads.tests.factories import create_user


class ProfileTests(TestCase):
    def setUp(self):
        self.user = create_user(username="profile", password="password123", email="old@example.com")
        self.other = create_user(username="other-profile", email="other@example.com")

    def test_profile_requires_authentication(self):
        response = self.client.get(reverse("leads:profile"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_profile_get_shows_user_data(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("leads:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "profile")

    def test_valid_profile_update_changes_basic_fields(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("leads:profile"),
            {
                "username": "profile-new",
                "first_name": "Novo",
                "last_name": "Nome",
                "email": "new@example.com",
            },
        )
        self.assertRedirects(response, reverse("leads:profile"))
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "profile-new")
        self.assertEqual(self.user.email, "new@example.com")

    def test_invalid_email_keeps_form_on_page(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("leads:profile"),
            {"username": "profile", "first_name": "", "last_name": "", "email": "invalid"},
        )
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "old@example.com")

    def test_duplicate_username_is_rejected(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("leads:profile"),
            {"username": self.other.username, "first_name": "", "last_name": "", "email": "new@example.com"},
        )
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "profile")

    def test_profile_post_does_not_change_sensitive_fields(self):
        self.client.force_login(self.user)
        old_password = self.user.password
        response = self.client.post(
            reverse("leads:profile"),
            {
                "username": "profile",
                "first_name": "Safe",
                "last_name": "User",
                "email": "safe@example.com",
                "is_staff": "on",
                "is_superuser": "on",
                "password": "plain-text",
                "groups": "1",
                "user_permissions": "1",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)
        self.assertEqual(self.user.password, old_password)

    def test_user_cannot_update_other_profile_through_profile_route(self):
        self.client.force_login(self.user)
        self.client.post(
            reverse("leads:profile"),
            {"username": "profile", "first_name": "Mine", "last_name": "", "email": "mine@example.com"},
        )
        self.other.refresh_from_db()
        self.assertEqual(self.other.email, "other@example.com")
