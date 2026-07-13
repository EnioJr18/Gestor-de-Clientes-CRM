from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from apps.leads.models import Interaction, Lead
from apps.leads.tests.factories import create_interaction, create_lead, create_user, lead_payload, set_created_at


class ApiTestMixin:
    def setUp(self):
        self.user = create_user(username="apiuser", password="password123", email="api@example.com")
        self.other = create_user(username="otherapi", password="password123", email="other@example.com")
        self.client = APIClient()

    def login(self, user=None):
        self.client.force_authenticate(user or self.user)


class HealthApiTests(APITestCase):
    def test_health_is_public_and_minimal(self):
        response = self.client.get(reverse("api_v1:health"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"status": "ok"})
        self.assertNotIn("database", response.content.decode().lower())


class CurrentUserApiTests(ApiTestMixin, APITestCase):
    def test_me_requires_authentication(self):
        response = self.client.get(reverse("api_v1:users_me"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json()["code"], "not_authenticated")

    def test_me_returns_only_safe_fields(self):
        self.login()

        response = self.client.get(reverse("api_v1:users_me"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(response.json()),
            {"id", "username", "first_name", "last_name", "email"},
        )
        self.assertEqual(response.json()["username"], "apiuser")
        self.assertNotIn("password", response.json())
        self.assertNotIn("is_superuser", response.json())


class LeadListApiTests(ApiTestMixin, APITestCase):
    def test_list_requires_authentication(self):
        response = self.client.get(reverse("api_v1:lead-list"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json()["code"], "not_authenticated")

    def test_empty_list_is_paginated(self):
        self.login()

        response = self.client.get(reverse("api_v1:lead-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], 0)
        self.assertEqual(response.json()["results"], [])

    def test_list_is_isolated_and_ordered_by_created_descending(self):
        older = create_lead(user=self.user, nome="Older", email="older@example.com")
        newer = create_lead(user=self.user, nome="Newer", email="newer@example.com")
        create_lead(user=self.other, nome="Other", email="otherlead@example.com")
        set_created_at(older, timezone.now() - timedelta(days=2))
        set_created_at(newer, timezone.now())
        self.login()

        response = self.client.get(reverse("api_v1:lead-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [item["nome"] for item in response.json()["results"]]
        self.assertEqual(names, ["Newer", "Older"])

    def test_pagination_search_filters_and_ordering_work_together(self):
        set_created_at(
            create_lead(
                user=self.user,
                nome="Ana",
                sobrenome="Filtro",
                email="ana@example.com",
                telefone="111",
                status=Lead.STATUS_NOVO,
                prioridade=Lead.PRIORITY_ALTA,
            ),
            timezone.now() - timedelta(days=1),
        )
        create_lead(
            user=self.user,
            nome="Bruno",
            sobrenome="Fora",
            email="bruno@example.com",
            telefone="222",
            status=Lead.STATUS_VENDIDO,
            prioridade=Lead.PRIORITY_BAIXA,
        )
        self.login()

        response = self.client.get(
            reverse("api_v1:lead-list"),
            {
                "search": "ana",
                "status": Lead.STATUS_NOVO,
                "prioridade": Lead.PRIORITY_ALTA,
                "ordering": "nome",
                "page_size": "1",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(response.json()["results"][0]["email"], "ana@example.com")

    def test_invalid_filters_return_standard_errors(self):
        self.login()

        cases = [
            {"status": "INVALIDO"},
            {"prioridade": "INVALIDA"},
            {"criado_em_de": "not-a-date"},
            {"criado_em_de": "2026-12-31", "criado_em_ate": "2026-01-01"},
            {"ordering": "agente_responsavel"},
            {"foo": "bar"},
        ]

        for params in cases:
            with self.subTest(params=params):
                response = self.client.get(reverse("api_v1:lead-list"), params)
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                body = response.json()
                self.assertEqual(body["code"], "validation_error")
                self.assertIn("errors", body)

        response = self.client.get(reverse("api_v1:lead-list"), {"page": "abc"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()["code"], "not_found")

    def test_page_size_above_max_is_capped(self):
        for index in range(101):
            create_lead(user=self.user, nome=f"Lead {index}", email=f"lead{index}@example.com")
        self.login()

        response = self.client.get(reverse("api_v1:lead-list"), {"page_size": "999"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 100)


class LeadCreateApiTests(ApiTestMixin, APITestCase):
    def test_valid_create_assigns_owner_and_normalizes_email(self):
        self.login()
        payload = lead_payload(email="  NOVO@EXAMPLE.COM  ")

        response = self.client.post(reverse("api_v1:lead-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        lead = Lead.objects.get()
        self.assertEqual(lead.agente_responsavel, self.user)
        self.assertEqual(lead.email, "novo@example.com")
        self.assertNotIn("agente_responsavel", response.json())

    def test_create_validation_errors(self):
        self.login()

        cases = [
            lead_payload(nome=""),
            lead_payload(nome="   "),
            lead_payload(email="invalid"),
            lead_payload(status="INVALIDO"),
            lead_payload(prioridade="INVALIDA"),
            lead_payload(nome="x" * 256),
            lead_payload(is_staff=True),
            lead_payload(agente_responsavel=self.other.pk),
            lead_payload(criado_em="2026-01-01T00:00:00Z"),
        ]

        for payload in cases:
            with self.subTest(payload=payload):
                response = self.client.post(reverse("api_v1:lead-list"), payload, format="json")
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertEqual(response.json()["code"], "validation_error")

    def test_duplicate_email_same_user_is_rejected_case_insensitive(self):
        create_lead(user=self.user, email="dup@example.com")
        self.login()

        response = self.client.post(
            reverse("api_v1:lead-list"),
            lead_payload(email="DUP@example.com"),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.json()["errors"])

    def test_same_email_for_different_users_is_allowed(self):
        create_lead(user=self.other, email="shared@example.com")
        self.login()

        response = self.client.post(
            reverse("api_v1:lead-list"),
            lead_payload(email="shared@example.com"),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_unauthenticated_create_is_rejected(self):
        response = self.client.post(reverse("api_v1:lead-list"), lead_payload(), format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_session_create_requires_csrf(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="apiuser", password="password123"))

        response = client.post(reverse("api_v1:lead-list"), lead_payload(), format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()["code"], "permission_denied")

    def test_session_create_accepts_valid_csrf_token(self):
        client = APIClient(enforce_csrf_checks=True)
        client.get(reverse("login"))
        csrf_token = client.cookies["csrftoken"].value
        self.assertTrue(client.login(username="apiuser", password="password123"))

        response = client.post(
            reverse("api_v1:lead-list"),
            lead_payload(email="csrf@example.com"),
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class LeadDetailApiTests(ApiTestMixin, APITestCase):
    def setUp(self):
        super().setUp()
        self.lead = create_lead(user=self.user, nome="Own", email="own@example.com")
        self.other_lead = create_lead(user=self.other, nome="Other", email="otherlead@example.com")

    def test_detail_for_own_lead(self):
        self.login()

        response = self.client.get(reverse("api_v1:lead-detail", args=[self.lead.pk]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["email"], "own@example.com")

    def test_detail_for_missing_or_other_lead_is_404(self):
        self.login()

        for pk in [999999, self.other_lead.pk]:
            with self.subTest(pk=pk):
                response = self.client.get(reverse("api_v1:lead-detail", args=[pk]))
                self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
                self.assertEqual(response.json()["code"], "not_found")

    def test_patch_updates_partial_payload_and_rejects_protected_fields(self):
        self.login()

        response = self.client.patch(
            reverse("api_v1:lead-detail", args=[self.lead.pk]),
            {"nome": "Atualizado"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lead.refresh_from_db()
        self.assertEqual(self.lead.nome, "Atualizado")

        protected = self.client.patch(
            reverse("api_v1:lead-detail", args=[self.lead.pk]),
            {"agente_responsavel": self.other.pk},
            format="json",
        )
        self.assertEqual(protected.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.lead.agente_responsavel, self.user)

    def test_patch_duplicate_email_is_rejected(self):
        create_lead(user=self.user, email="taken@example.com")
        self.login()

        response = self.client.patch(
            reverse("api_v1:lead-detail", args=[self.lead.pk]),
            {"email": "TAKEN@example.com"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.json()["errors"])

    def test_patch_other_user_lead_is_404(self):
        self.login()

        response = self.client.patch(
            reverse("api_v1:lead-detail", args=[self.other_lead.pk]),
            {"nome": "Hack"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_own_lead_cascades_interactions(self):
        interaction = create_interaction(lead=self.lead)
        self.login()

        response = self.client.delete(reverse("api_v1:lead-detail", args=[self.lead.pk]))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Lead.objects.filter(pk=self.lead.pk).exists())
        self.assertFalse(Interaction.objects.filter(pk=interaction.pk).exists())

    def test_delete_other_user_lead_is_404(self):
        self.login()

        response = self.client.delete(reverse("api_v1:lead-detail", args=[self.other_lead.pk]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_method_not_allowed_uses_standard_error(self):
        self.login()

        response = self.client.post(reverse("api_v1:lead-detail", args=[self.lead.pk]), {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.json()["code"], "method_not_allowed")


class ApiSchemaAndLegacyRouteTests(ApiTestMixin, APITestCase):
    def test_schema_and_docs_routes_respond(self):
        for name in ["schema", "swagger-ui", "redoc"]:
            with self.subTest(name=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_legacy_routes_still_respond(self):
        self.client.force_login(self.user)

        routes = [
            reverse("login"),
            reverse("leads:dashboard"),
            reverse("leads:lead_list"),
            reverse("leads:lead_create"),
            reverse("admin:login"),
        ]

        for route in routes:
            with self.subTest(route=route):
                response = self.client.get(route)
                self.assertLess(response.status_code, 500)
