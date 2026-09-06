import logging
from datetime import timedelta

from django.conf import settings
from django.core.cache import cache
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from apps.accounts.api.throttles import CsrfRateThrottle, LoginRateThrottle, RefreshRateThrottle
from apps.leads.models import Lead
from apps.leads.tests.factories import create_lead, create_user, lead_payload


class JwtApiMixin:
    def setUp(self):
        cache.clear()
        self.user = create_user(username="jwtuser", password="password123", email="jwt@example.com")
        self.other = create_user(username="jwtother", password="password123", email="other@example.com")
        self.client = APIClient(enforce_csrf_checks=True)

    def csrf(self, client=None):
        client = client or self.client
        response = client.get(reverse("accounts_api:csrf"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.json()["csrfToken"]

    def login(self, client=None, user=None):
        client = client or self.client
        user = user or self.user
        csrf = self.csrf(client)
        response = client.post(
            reverse("accounts_api:login"),
            {"username": user.username, "password": "password123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response, csrf

    def bearer(self, token, client=None):
        (client or self.client).credentials(HTTP_AUTHORIZATION=f"Bearer {token}")


class CompatibilityTests(JwtApiMixin, APITestCase):
    def test_import_emission_validation_refresh_and_blacklist(self):
        refresh = RefreshToken.for_user(self.user)
        access = str(refresh.access_token)

        validated = JWTAuthentication().get_validated_token(access)
        self.assertEqual(validated["user_id"], str(self.user.pk))

        refresh.blacklist()
        self.assertTrue(BlacklistedToken.objects.filter(token__jti=refresh["jti"]).exists())
        with self.assertRaises(Exception):
            RefreshToken(str(refresh))


class LoginTests(JwtApiMixin, APITestCase):
    def test_login_returns_access_user_and_http_only_refresh_cookie(self):
        response, _ = self.login()

        self.assertEqual(set(response.json()), {"access", "token_type", "expires_in", "user"})
        self.assertEqual(response.json()["token_type"], "Bearer")
        self.assertEqual(response.json()["expires_in"], 300)
        self.assertNotIn("refresh", response.json())
        cookie = response.cookies[settings.JWT_REFRESH_COOKIE_NAME]
        self.assertTrue(cookie["httponly"])
        self.assertEqual(cookie["samesite"], "Lax")
        self.assertEqual(cookie["path"], "/api/v1/auth/")
        self.assertFalse(bool(cookie["secure"]))

    def test_invalid_unknown_wrong_password_and_inactive_are_generic(self):
        inactive = create_user(username="inactive", password="password123")
        inactive.is_active = False
        inactive.save(update_fields=["is_active"])
        cases = [
            {"username": "missing", "password": "password123"},
            {"username": self.user.username, "password": "wrong"},
            {"username": inactive.username, "password": "password123"},
        ]
        for payload in cases:
            with self.subTest(payload=payload):
                response = self.client.post(reverse("accounts_api:login"), payload, format="json")
                self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
                self.assertEqual(response.json()["code"], "authentication_failed")
                self.assertEqual(response.json()["message"], "Credenciais invalidas.")

    def test_missing_blank_and_extra_fields_are_rejected(self):
        cases = [
            {},
            {"username": "", "password": "password123"},
            {"username": self.user.username, "password": ""},
            {"username": self.user.username, "password": "password123", "is_staff": True},
            {"username": self.user.username, "password": "password123", "refresh": "x"},
        ]
        for payload in cases:
            with self.subTest(payload=payload):
                response = self.client.post(reverse("accounts_api:login"), payload, format="json")
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertEqual(response.json()["code"], "validation_error")

    def test_login_rejects_form_encoded_payloads(self):
        response = self.client.post(
            reverse("accounts_api:login"),
            {"username": self.user.username, "password": "password123"},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        self.assertEqual(response.json()["code"], "unsupported_media_type")
        self.assertNotIn(settings.JWT_REFRESH_COOKIE_NAME, response.cookies)

    def test_wrong_method_uses_standard_contract(self):
        response = self.client.get(reverse("accounts_api:login"))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.json()["code"], "method_not_allowed")


class RefreshTests(JwtApiMixin, APITestCase):
    def test_refresh_requires_csrf_rotates_blacklists_and_updates_cookie(self):
        login, csrf = self.login()
        old_raw = login.cookies[settings.JWT_REFRESH_COOKIE_NAME].value
        old_jti = RefreshToken(old_raw)["jti"]

        missing_csrf = self.client.post(reverse("accounts_api:refresh"), {}, format="json")
        self.assertEqual(missing_csrf.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(missing_csrf.json()["code"], "csrf_failed")

        response = self.client.post(
            reverse("accounts_api:refresh"), {}, format="json", HTTP_X_CSRFTOKEN=csrf
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.json()), {"access", "token_type", "expires_in"})
        self.assertNotIn("refresh", response.json())
        new_raw = response.cookies[settings.JWT_REFRESH_COOKIE_NAME].value
        self.assertNotEqual(old_raw, new_raw)
        self.assertTrue(BlacklistedToken.objects.filter(token__jti=old_jti).exists())

        self.client.cookies[settings.JWT_REFRESH_COOKIE_NAME] = old_raw
        rejected = self.client.post(
            reverse("accounts_api:refresh"), {}, format="json", HTTP_X_CSRFTOKEN=csrf
        )
        self.assertEqual(rejected.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(rejected.json()["code"], "authentication_failed")

    def test_missing_invalid_expired_and_extra_payload_are_rejected(self):
        csrf = self.csrf()
        missing = self.client.post(
            reverse("accounts_api:refresh"), {}, format="json", HTTP_X_CSRFTOKEN=csrf
        )
        self.assertEqual(missing.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.cookies[settings.JWT_REFRESH_COOKIE_NAME] = "malformed"
        invalid = self.client.post(
            reverse("accounts_api:refresh"), {}, format="json", HTTP_X_CSRFTOKEN=csrf
        )
        self.assertEqual(invalid.status_code, status.HTTP_401_UNAUTHORIZED)

        expired = RefreshToken.for_user(self.user)
        expired.set_exp(lifetime=timedelta(seconds=-1))
        self.client.cookies[settings.JWT_REFRESH_COOKIE_NAME] = str(expired)
        expired_response = self.client.post(
            reverse("accounts_api:refresh"), {}, format="json", HTTP_X_CSRFTOKEN=csrf
        )
        self.assertEqual(expired_response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.cookies[settings.JWT_REFRESH_COOKIE_NAME] = str(RefreshToken.for_user(self.user))
        extra = self.client.post(
            reverse("accounts_api:refresh"), {"refresh": "forbidden"}, format="json", HTTP_X_CSRFTOKEN=csrf
        )
        self.assertEqual(extra.status_code, status.HTTP_400_BAD_REQUEST)

    def test_refresh_rejects_user_deactivated_after_issuance(self):
        _, csrf = self.login()
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])
        response = self.client.post(
            reverse("accounts_api:refresh"), {}, format="json", HTTP_X_CSRFTOKEN=csrf
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_ignores_expired_access_header_and_uses_cookie(self):
        _, csrf = self.login()
        expired = AccessToken.for_user(self.user)
        expired.set_exp(lifetime=timedelta(seconds=-1))
        self.bearer(str(expired))
        response = self.client.post(
            reverse("accounts_api:refresh"), {}, format="json", HTTP_X_CSRFTOKEN=csrf
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_concurrent_reuse_of_rotated_token_fails(self):
        login, csrf = self.login()
        old_raw = login.cookies[settings.JWT_REFRESH_COOKIE_NAME].value
        first = self.client.post(reverse("accounts_api:refresh"), {}, format="json", HTTP_X_CSRFTOKEN=csrf)
        self.assertEqual(first.status_code, status.HTTP_200_OK)
        self.client.cookies[settings.JWT_REFRESH_COOKIE_NAME] = old_raw
        second = self.client.post(reverse("accounts_api:refresh"), {}, format="json", HTTP_X_CSRFTOKEN=csrf)
        self.assertEqual(second.status_code, status.HTTP_401_UNAUTHORIZED)


class LogoutTests(JwtApiMixin, APITestCase):
    def test_logout_requires_csrf_revokes_and_deletes_cookie(self):
        login, csrf = self.login()
        raw = login.cookies[settings.JWT_REFRESH_COOKIE_NAME].value
        jti = RefreshToken(raw)["jti"]

        denied = self.client.post(reverse("accounts_api:logout"), {}, format="json")
        self.assertEqual(denied.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.post(
            reverse("accounts_api:logout"), {}, format="json", HTTP_X_CSRFTOKEN=csrf
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.cookies[settings.JWT_REFRESH_COOKIE_NAME]["max-age"], 0)
        self.assertTrue(BlacklistedToken.objects.filter(token__jti=jti).exists())

    def test_logout_is_idempotent_with_valid_csrf(self):
        csrf = self.csrf()
        for _ in range(2):
            response = self.client.post(
                reverse("accounts_api:logout"), {}, format="json", HTTP_X_CSRFTOKEN=csrf
            )
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class CurrentUserTests(JwtApiMixin, APITestCase):
    def test_me_accepts_jwt_and_returns_only_safe_fields(self):
        access = str(RefreshToken.for_user(self.user).access_token)
        self.bearer(access)
        response = self.client.get(reverse("api_v1:users_me"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.json()), {"id", "username", "first_name", "last_name", "email"})

    def test_me_accepts_legacy_session(self):
        client = APIClient()
        self.assertTrue(client.login(username=self.user.username, password="password123"))
        response = client.get(reverse("api_v1:users_me"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_me_rejects_missing_invalid_expired_and_inactive_tokens(self):
        response = self.client.get(reverse("api_v1:users_me"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        for token in ["invalid", self.expired_access()]:
            with self.subTest(token=token):
                self.bearer(token)
                response = self.client.get(reverse("api_v1:users_me"))
                self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
                self.assertEqual(response.json()["code"], "authentication_failed")

        valid = str(RefreshToken.for_user(self.user).access_token)
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])
        self.bearer(valid)
        inactive = self.client.get(reverse("api_v1:users_me"))
        self.assertEqual(inactive.status_code, status.HTTP_401_UNAUTHORIZED)

    def expired_access(self):
        token = AccessToken.for_user(self.user)
        token.set_exp(lifetime=timedelta(seconds=-1))
        return str(token)


class JwtLeadCrudTests(JwtApiMixin, APITestCase):
    def test_jwt_can_list_create_update_and_delete_without_csrf(self):
        own = create_lead(user=self.user, email="ownjwt@example.com")
        create_lead(user=self.other, email="hiddenjwt@example.com")
        access = str(RefreshToken.for_user(self.user).access_token)
        client = APIClient(enforce_csrf_checks=True)
        self.bearer(access, client)

        listed = client.get(reverse("api_v1:lead-list"))
        self.assertEqual(listed.status_code, status.HTTP_200_OK)
        self.assertEqual(listed.json()["count"], 1)

        created = client.post(reverse("api_v1:lead-list"), lead_payload(email="createdjwt@example.com"), format="json")
        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        created_id = created.json()["id"]

        updated = client.patch(reverse("api_v1:lead-detail", args=[created_id]), {"nome": "JWT"}, format="json")
        self.assertEqual(updated.status_code, status.HTTP_200_OK)

        deleted = client.delete(reverse("api_v1:lead-detail", args=[own.pk]))
        self.assertEqual(deleted.status_code, status.HTTP_204_NO_CONTENT)

    def test_other_users_jwt_preserves_isolation(self):
        lead = create_lead(user=self.user, email="isolatedjwt@example.com")
        self.bearer(str(RefreshToken.for_user(self.other).access_token))
        response = self.client.get(reverse("api_v1:lead-detail", args=[lead.pk]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CorsTests(JwtApiMixin, APITestCase):
    def test_allowed_origin_credentials_and_preflight(self):
        origin = "http://localhost:5173"
        response = self.client.options(
            reverse("accounts_api:refresh"),
            HTTP_ORIGIN=origin,
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
            HTTP_ACCESS_CONTROL_REQUEST_HEADERS="authorization,x-csrftoken,content-type",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Access-Control-Allow-Origin"], origin)
        self.assertEqual(response["Access-Control-Allow-Credentials"], "true")
        self.assertIn("x-csrftoken", response["Access-Control-Allow-Headers"])

    def test_disallowed_origin_has_no_allow_origin_header(self):
        response = self.client.get(reverse("accounts_api:csrf"), HTTP_ORIGIN="https://evil.example")
        self.assertNotIn("Access-Control-Allow-Origin", response)


class CookieProductionPolicyTests(APITestCase):
    @override_settings(
        JWT_REFRESH_COOKIE_SECURE=True,
        JWT_REFRESH_COOKIE_SAMESITE="None",
        JWT_REFRESH_COOKIE_DOMAIN="crm.example.com",
    )
    def test_cookie_helper_uses_production_flags(self):
        user = create_user(username="prodflags", password="password123")
        client = APIClient()
        client.get(reverse("accounts_api:csrf"))
        response = client.post(
            reverse("accounts_api:login"),
            {"username": user.username, "password": "password123"},
            format="json",
        )
        cookie = response.cookies[settings.JWT_REFRESH_COOKIE_NAME]
        self.assertTrue(cookie["secure"])
        self.assertTrue(cookie["httponly"])
        self.assertEqual(cookie["samesite"], "None")
        self.assertEqual(cookie["domain"], "crm.example.com")


class AuthThrottleTests(JwtApiMixin, APITestCase):
    def test_login_throttle_returns_standard_429(self):
        cache.clear()
        original_rate = getattr(LoginRateThrottle, "rate", None)
        LoginRateThrottle.rate = "1/min"
        try:
            url = reverse("accounts_api:login")
            first = self.client.post(url, {"username": "none", "password": "wrong"}, format="json")
            self.assertEqual(first.status_code, status.HTTP_401_UNAUTHORIZED)
            second = self.client.post(url, {"username": "none", "password": "wrong"}, format="json")
            self.assertEqual(second.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
            self.assertEqual(second.json()["code"], "throttled")
            self.assertIsNotNone(second.get("Retry-After"))
        finally:
            if original_rate is None:
                delattr(LoginRateThrottle, "rate")
            else:
                LoginRateThrottle.rate = original_rate

    def test_refresh_and_csrf_throttles_return_429_and_retry_after(self):
        _, csrf = self.login()
        original_refresh_rate = getattr(RefreshRateThrottle, "rate", None)
        original_csrf_rate = getattr(CsrfRateThrottle, "rate", None)
        RefreshRateThrottle.rate = "1/min"
        CsrfRateThrottle.rate = "1/min"
        try:
            cache.clear()
            first_refresh = self.client.post(
                reverse("accounts_api:refresh"), {}, format="json", HTTP_X_CSRFTOKEN=csrf
            )
            second_refresh = self.client.post(
                reverse("accounts_api:refresh"), {}, format="json", HTTP_X_CSRFTOKEN=csrf
            )
            self.assertEqual(first_refresh.status_code, status.HTTP_200_OK)
            self.assertEqual(second_refresh.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
            self.assertIsNotNone(second_refresh.get("Retry-After"))

            cache.clear()
            first_csrf = self.client.get(reverse("accounts_api:csrf"))
            second_csrf = self.client.get(reverse("accounts_api:csrf"))
            self.assertEqual(first_csrf.status_code, status.HTTP_200_OK)
            self.assertEqual(second_csrf.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
            self.assertIsNotNone(second_csrf.get("Retry-After"))
        finally:
            cache.clear()
            if original_refresh_rate is None:
                delattr(RefreshRateThrottle, "rate")
            else:
                RefreshRateThrottle.rate = original_refresh_rate
            if original_csrf_rate is None:
                delattr(CsrfRateThrottle, "rate")
            else:
                CsrfRateThrottle.rate = original_csrf_rate


class TokenSecrecyTests(JwtApiMixin, APITestCase):
    def test_refresh_never_appears_in_login_or_refresh_json(self):
        login, csrf = self.login()
        self.assertNotIn("refresh", login.json())
        refresh = self.client.post(reverse("accounts_api:refresh"), {}, format="json", HTTP_X_CSRFTOKEN=csrf)
        self.assertNotIn("refresh", refresh.json())
        self.assertGreaterEqual(OutstandingToken.objects.filter(user=self.user).count(), 2)

    def test_refresh_token_is_not_written_to_logs(self):
        messages = []

        class CaptureHandler(logging.Handler):
            def emit(self, record):
                messages.append(record.getMessage())

        handler = CaptureHandler()
        root_logger = logging.getLogger()
        root_logger.addHandler(handler)
        try:
            response, _ = self.login()
        finally:
            root_logger.removeHandler(handler)

        raw_refresh = response.cookies[settings.JWT_REFRESH_COOKIE_NAME].value
        self.assertNotIn(raw_refresh, "\n".join(messages))
