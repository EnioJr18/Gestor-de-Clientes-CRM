from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.leads.models import Lead
from apps.leads.tests.factories import create_lead, create_user, set_created_at


class DashboardSummaryApiTests(APITestCase):
    def setUp(self):
        self.user = create_user(username="dashboard-api")
        self.other = create_user(username="dashboard-other")
        self.url = reverse("api_v1:dashboard-summary")

    def test_requires_authentication(self):
        self.assertEqual(self.client.get(self.url).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_jwt_and_session_authentication_are_accepted(self):
        jwt_client = APIClient()
        jwt_client.credentials(HTTP_AUTHORIZATION=f"Bearer {RefreshToken.for_user(self.user).access_token}")
        self.assertEqual(jwt_client.get(self.url).status_code, status.HTTP_200_OK)

        session_client = APIClient()
        self.assertTrue(session_client.login(username=self.user.username, password="password123"))
        self.assertEqual(session_client.get(self.url).status_code, status.HTTP_200_OK)

    def test_inactive_user_is_rejected_for_jwt_and_existing_session(self):
        session_client = APIClient()
        self.assertTrue(session_client.login(username=self.user.username, password="password123"))
        access = str(RefreshToken.for_user(self.user).access_token)
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])

        jwt_client = APIClient()
        jwt_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        self.assertEqual(jwt_client.get(self.url).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(session_client.get(self.url).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_metrics_aggregation_recent_and_isolation(self):
        now = timezone.now()
        own = set_created_at(create_lead(user=self.user, status=Lead.STATUS_VENDIDO, prioridade=Lead.PRIORITY_ALTA), now - timedelta(minutes=1))
        newest = set_created_at(create_lead(user=self.user, status=Lead.STATUS_NOVO, prioridade=Lead.PRIORITY_BAIXA), now)
        set_created_at(create_lead(user=self.other, status=Lead.STATUS_VENDIDO), now)
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url, {"period": "30d"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["metrics"], {"total_leads": 2, "created_today": 2, "created_in_period": 2, "converted_in_period": 1, "conversion_rate": 50.0})
        self.assertEqual(response.data["recent_leads"][0]["id"], newest.id)
        self.assertEqual({item["id"] for item in response.data["recent_leads"]}, {own.id, newest.id})
        self.assertEqual(sum(item["count"] for item in response.data["by_status"]), 2)

    def test_period_validation_and_zero_months(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url, {"period": "custom", "date_from": "2026-01-01", "date_to": "2026-03-31"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([item["count"] for item in response.data["monthly_evolution"]], [0, 0, 0])
        self.assertEqual(self.client.get(self.url, {"period": "invalid"}).status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.client.get(self.url, {"period": "custom", "date_from": "2026-03-01"}).status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.client.get(self.url, {"period": "custom", "date_from": "2026-03-02", "date_to": "2026-03-01"}).status_code, status.HTTP_400_BAD_REQUEST)

    def test_recent_leads_are_limited_and_do_not_expose_owner(self):
        now = timezone.now()
        for index in range(6):
            set_created_at(create_lead(user=self.user), now - timedelta(minutes=index))
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["recent_leads"]), 5)
        self.assertNotIn("agente_responsavel", response.data["recent_leads"][0])

    def test_custom_period_is_inclusive_and_has_zero_conversion_rate(self):
        today = timezone.localdate()
        now = timezone.now()
        set_created_at(create_lead(user=self.user, status=Lead.STATUS_NOVO), now)
        self.client.force_authenticate(self.user)
        response = self.client.get(
            self.url,
            {"period": "custom", "date_from": today.isoformat(), "date_to": today.isoformat()},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["metrics"]["created_in_period"], 1)
        self.assertEqual(response.data["metrics"]["converted_in_period"], 0)
        self.assertEqual(response.data["metrics"]["conversion_rate"], 0.0)

    def test_status_and_priority_include_all_choices_with_stable_labels(self):
        create_lead(user=self.user, status=Lead.STATUS_VENDIDO, prioridade=Lead.PRIORITY_ALTA)
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [(item["status"], item["label"]) for item in response.data["by_status"]],
            list(Lead.STATUS_CHOICES),
        )
        self.assertEqual(
            [(item["priority"], item["label"]) for item in response.data["by_priority"]],
            list(Lead.PRIORITY_CHOICES),
        )
        self.assertEqual(next(item["count"] for item in response.data["by_status"] if item["status"] == Lead.STATUS_VENDIDO), 1)
        self.assertEqual(next(item["count"] for item in response.data["by_priority"] if item["priority"] == Lead.PRIORITY_ALTA), 1)

    def test_predefined_periods_and_twelve_month_evolution(self):
        now = timezone.now()
        set_created_at(create_lead(user=self.user), now - timedelta(days=8))
        set_created_at(create_lead(user=self.user), now - timedelta(days=31))
        self.client.force_authenticate(self.user)
        self.assertEqual(self.client.get(self.url, {"period": "7d"}).data["metrics"]["created_in_period"], 0)
        self.assertEqual(self.client.get(self.url, {"period": "30d"}).data["metrics"]["created_in_period"], 1)
        self.assertEqual(self.client.get(self.url, {"period": "90d"}).data["metrics"]["created_in_period"], 2)
        self.assertEqual(self.client.get(self.url).data["period"]["key"], "30d")
        response = self.client.get(self.url, {"period": "12m"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["monthly_evolution"]), 12)
        self.assertEqual(response.data["monthly_evolution"], sorted(response.data["monthly_evolution"], key=lambda item: item["month"]))

    def test_custom_period_rejects_invalid_dates_and_excessive_range(self):
        self.client.force_authenticate(self.user)
        cases = [
            {"period": "custom", "date_from": "not-a-date", "date_to": "2026-01-01"},
            {"period": "custom", "date_from": "2025-01-01", "date_to": "2026-01-03"},
            {"period": "custom", "date_from": "2026-01-01"},
            {"period": "custom", "date_to": "2026-01-01"},
        ]
        for params in cases:
            with self.subTest(params=params):
                response = self.client.get(self.url, params)
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertEqual(response.data["status"], 400)
                self.assertEqual(response.data["code"], "validation_error")

    def test_conversion_rate_is_rounded_to_one_decimal(self):
        create_lead(user=self.user, status=Lead.STATUS_VENDIDO)
        create_lead(user=self.user, status=Lead.STATUS_NOVO)
        create_lead(user=self.user, status=Lead.STATUS_NOVO)
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["metrics"]["conversion_rate"], 33.3)
