from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.leads.models import Interaction
from apps.leads.tests.factories import create_interaction, create_lead, create_user


class InteractionApiTests(APITestCase):
    def setUp(self):
        self.user = create_user(username="interaction-api", password="password123")
        self.other = create_user(username="interaction-other", password="password123")
        self.lead = create_lead(user=self.user, email="interaction-api@example.com")
        self.second_lead = create_lead(user=self.user, email="interaction-second@example.com")
        self.other_lead = create_lead(user=self.other, email="interaction-other@example.com")
        self.client = APIClient()

    def login(self, user=None):
        self.client.force_authenticate(user or self.user)

    def list_url(self, lead=None):
        return reverse("api_v1:interaction-list", kwargs={"lead_id": (lead or self.lead).pk})

    def detail_url(self, interaction, lead=None):
        return reverse(
            "api_v1:interaction-detail",
            kwargs={"lead_id": (lead or self.lead).pk, "pk": interaction.pk},
        )

    def payload(self, **overrides):
        data = {
            "tipo": Interaction.TIPO_LIGACAO,
            "data_interacao": "2026-09-04T14:30:00-03:00",
            "nota": "Cliente pediu retorno.",
        }
        data.update(overrides)
        return data

    def test_authentication_is_required(self):
        response = self.client.get(self.list_url())

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json()["code"], "not_authenticated")

    def test_create_interaction_for_own_lead(self):
        self.login()

        response = self.client.post(self.list_url(), self.payload(), format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        interaction = Interaction.objects.get()
        self.assertEqual(interaction.lead, self.lead)
        self.assertEqual(interaction.tipo, Interaction.TIPO_LIGACAO)
        self.assertEqual(interaction.nota, "Cliente pediu retorno.")
        self.assertIsNotNone(interaction.criado_em)
        self.assertIsNotNone(interaction.atualizado_em)
        self.assertNotIn("lead", response.json())

    def test_create_uses_server_time_when_interaction_date_is_omitted(self):
        self.login()

        response = self.client.post(
            self.list_url(),
            self.payload(data_interacao=None),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(
            self.list_url(),
            {"tipo": Interaction.TIPO_NOTA, "nota": "Registro sem data explicita."},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(Interaction.objects.get().data_interacao)

    def test_create_validation_errors_are_standardized(self):
        self.login()
        cases = [
            self.payload(tipo=None),
            self.payload(tipo="INVALIDO"),
            self.payload(data_interacao="data-invalida"),
            self.payload(nota=""),
            self.payload(nota=" \n\t "),
            self.payload(lead=self.other_lead.pk),
            self.payload(criado_em="2026-09-04T14:30:00Z"),
            self.payload(campo_desconhecido=True),
        ]

        for payload in cases:
            with self.subTest(payload=payload):
                response = self.client.post(self.list_url(), payload, format="json")
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertEqual(response.json()["code"], "validation_error")

    def test_list_is_owned_and_deterministically_ordered(self):
        older = create_interaction(self.lead, nota="Mais antiga", tipo=Interaction.TIPO_NOTA)
        newer = create_interaction(self.lead, nota="Mais recente", tipo=Interaction.TIPO_EMAIL)
        create_interaction(self.other_lead, nota="De outro usuario")
        Interaction.objects.filter(pk=older.pk).update(data_interacao=timezone.now() - timedelta(days=1))
        Interaction.objects.filter(pk=newer.pk).update(data_interacao=timezone.now())
        self.login()

        response = self.client.get(self.list_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], 2)
        self.assertEqual([item["id"] for item in response.json()["results"]], [newer.pk, older.pk])

    def test_other_users_lead_is_hidden_for_list_and_create(self):
        self.login()

        listed = self.client.get(self.list_url(self.other_lead))
        created = self.client.post(self.list_url(self.other_lead), self.payload(), format="json")

        self.assertEqual(listed.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(created.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(Interaction.objects.exists())

    def test_detail_for_own_interaction(self):
        interaction = create_interaction(self.lead, tipo=Interaction.TIPO_REUNIAO)
        self.login()

        response = self.client.get(self.detail_url(interaction))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["id"], interaction.pk)
        self.assertEqual(response.json()["tipo"], Interaction.TIPO_REUNIAO)

    def test_missing_foreign_or_wrong_lead_interactions_are_hidden(self):
        own = create_interaction(self.lead)
        foreign = create_interaction(self.other_lead)
        self.login()

        cases = [
            self.detail_url(own, self.second_lead),
            self.detail_url(foreign, self.other_lead),
            reverse("api_v1:interaction-detail", kwargs={"lead_id": self.lead.pk, "pk": 999999}),
        ]
        for url in cases:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
                self.assertEqual(response.json()["code"], "not_found")

    def test_patch_updates_own_interaction_and_timestamp(self):
        interaction = create_interaction(self.lead, nota="Antes")
        old_timestamp = timezone.now() - timedelta(days=1)
        Interaction.objects.filter(pk=interaction.pk).update(atualizado_em=old_timestamp)
        self.login()

        response = self.client.patch(
            self.detail_url(interaction),
            {"tipo": Interaction.TIPO_MENSAGEM, "nota": "Depois"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        interaction.refresh_from_db()
        self.assertEqual(interaction.tipo, Interaction.TIPO_MENSAGEM)
        self.assertEqual(interaction.nota, "Depois")
        self.assertGreater(interaction.atualizado_em, old_timestamp)

    def test_patch_and_delete_foreign_interaction_return_404(self):
        foreign = create_interaction(self.other_lead, nota="Nao tocar")
        self.login()

        patched = self.client.patch(self.detail_url(foreign, self.other_lead), {"nota": "Hack"}, format="json")
        deleted = self.client.delete(self.detail_url(foreign, self.other_lead))

        self.assertEqual(patched.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(deleted.status_code, status.HTTP_404_NOT_FOUND)
        foreign.refresh_from_db()
        self.assertEqual(foreign.nota, "Nao tocar")

    def test_delete_own_interaction(self):
        interaction = create_interaction(self.lead)
        self.login()

        response = self.client.delete(self.detail_url(interaction))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Interaction.objects.filter(pk=interaction.pk).exists())
