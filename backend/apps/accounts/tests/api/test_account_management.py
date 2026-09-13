from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.api.throttles import RegistrationRateThrottle
from apps.leads.tests.factories import create_user


User = get_user_model()


class AccountManagementMixin:
    def setUp(self):
        cache.clear()
        self.user = create_user(username="account-user", password="CurrentPass123!", email="account@example.com")
        self.other = create_user(username="other-account", email="other@example.com")
        self.client = APIClient()

    def authenticate(self):
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        return refresh

    def registration_payload(self, **overrides):
        payload = {
            "username": "new-account",
            "email": "new@example.com",
            "first_name": "New",
            "last_name": "Account",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
        }
        payload.update(overrides)
        return payload


class RegistrationTests(AccountManagementMixin, APITestCase):
    def test_register_creates_active_user_normalizes_email_and_exposes_only_safe_fields(self):
        response = self.client.post(
            reverse("accounts_api:register"),
            self.registration_payload(email="  New.User@Example.COM  "),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(set(response.json()), {"id", "username", "first_name", "last_name", "email"})
        self.assertNotIn("password", response.json())
        self.assertNotIn("access", response.json())
        self.assertNotIn("refresh", response.json())
        user = User.objects.get(username="new-account")
        self.assertTrue(user.is_active)
        self.assertEqual(user.email, "new.user@example.com")
        self.assertTrue(user.check_password("StrongPass123!"))

    def test_registered_user_can_login(self):
        self.client.post(reverse("accounts_api:register"), self.registration_payload(), format="json")

        response = self.client.post(
            reverse("accounts_api:login"),
            {"username": "new-account", "password": "StrongPass123!"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_register_rejects_extra_fields_duplicate_username_invalid_email_and_password_errors(self):
        create_user(username="taken-account")
        cases = [
            (self.registration_payload(is_staff=True), "is_staff"),
            (self.registration_payload(username="taken-account"), "username"),
            (self.registration_payload(email="invalid"), "email"),
            (self.registration_payload(password="123", password_confirm="123"), "password"),
            (self.registration_payload(password_confirm="DifferentPass123!"), "password_confirm"),
        ]

        for payload, field in cases:
            with self.subTest(field=field):
                response = self.client.post(reverse("accounts_api:register"), payload, format="json")
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn(field, response.json()["errors"])

    def test_registration_throttle_uses_standard_429_contract(self):
        original_rate = getattr(RegistrationRateThrottle, "rate", None)
        RegistrationRateThrottle.rate = "1/min"
        try:
            first = self.client.post(reverse("accounts_api:register"), self.registration_payload(), format="json")
            second = self.client.post(
                reverse("accounts_api:register"),
                self.registration_payload(username="other-new-account", email="other-new@example.com"),
                format="json",
            )
            self.assertEqual(first.status_code, status.HTTP_201_CREATED)
            self.assertEqual(second.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
            self.assertEqual(second.json()["code"], "throttled")
            self.assertIsNotNone(second.get("Retry-After"))
        finally:
            cache.clear()
            if original_rate is None:
                delattr(RegistrationRateThrottle, "rate")
            else:
                RegistrationRateThrottle.rate = original_rate


class CurrentUserProfileTests(AccountManagementMixin, APITestCase):
    def test_get_current_user_contract_is_preserved(self):
        self.authenticate()

        response = self.client.get(reverse("api_v1:users_me"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.json()), {"id", "username", "first_name", "last_name", "email"})

    def test_patch_updates_only_authenticated_user_and_normalizes_email(self):
        self.authenticate()

        response = self.client.patch(
            reverse("api_v1:users_me"),
            {
                "username": "account-user-updated",
                "first_name": "Updated",
                "last_name": "Person",
                "email": "  Updated@Example.COM ",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["email"], "updated@example.com")
        self.user.refresh_from_db()
        self.other.refresh_from_db()
        self.assertEqual(self.user.username, "account-user-updated")
        self.assertEqual(self.user.email, "updated@example.com")
        self.assertEqual(self.other.email, "other@example.com")

    def test_patch_rejects_duplicate_username_and_privileged_fields(self):
        self.authenticate()

        duplicate = self.client.patch(
            reverse("api_v1:users_me"), {"username": self.other.username}, format="json"
        )
        privileged = self.client.patch(reverse("api_v1:users_me"), {"is_staff": True}, format="json")

        self.assertEqual(duplicate.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", duplicate.json()["errors"])
        self.assertEqual(privileged.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("is_staff", privileged.json()["errors"])
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_staff)

    def test_patch_requires_authentication(self):
        response = self.client.patch(reverse("api_v1:users_me"), {"first_name": "Nope"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ChangePasswordTests(AccountManagementMixin, APITestCase):
    def password_payload(self, **overrides):
        payload = {
            "current_password": "CurrentPass123!",
            "new_password": "ReplacementPass123!",
            "new_password_confirm": "ReplacementPass123!",
        }
        payload.update(overrides)
        return payload

    def test_change_password_updates_password_blacklists_refreshes_and_deletes_cookie(self):
        refresh = self.authenticate()
        second_refresh = RefreshToken.for_user(self.user)

        response = self.client.post(
            reverse("accounts_api:change-password"), self.password_payload(), format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b"")
        self.assertEqual(response.cookies["crm_refresh"]["max-age"], 0)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("ReplacementPass123!"))
        outstanding = OutstandingToken.objects.filter(user=self.user)
        self.assertGreaterEqual(outstanding.count(), 2)
        self.assertTrue(BlacklistedToken.objects.filter(token__in=outstanding).exists())
        self.assertTrue(BlacklistedToken.objects.filter(token__jti=refresh["jti"]).exists())
        self.assertTrue(BlacklistedToken.objects.filter(token__jti=second_refresh["jti"]).exists())

        # Access tokens are stateless and remain usable until their existing short TTL expires.
        current_access = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {current_access}")
        self.assertEqual(self.client.get(reverse("api_v1:users_me")).status_code, status.HTTP_200_OK)

    def test_change_password_rejects_invalid_current_new_and_confirmation_values(self):
        self.authenticate()
        cases = [
            (self.password_payload(current_password="wrong"), "current_password"),
            (self.password_payload(new_password="123", new_password_confirm="123"), "new_password"),
            (self.password_payload(new_password_confirm="DifferentPass123!"), "new_password_confirm"),
        ]

        for payload, field in cases:
            with self.subTest(field=field):
                response = self.client.post(reverse("accounts_api:change-password"), payload, format="json")
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn(field, response.json()["errors"])

    def test_change_password_requires_authentication(self):
        response = self.client.post(reverse("accounts_api:change-password"), self.password_payload(), format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
