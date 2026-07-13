from django.test import TestCase
from django.urls import reverse

from apps.leads.models import Interaction, Lead
from apps.leads.tests.factories import create_interaction, create_lead, create_user, lead_payload


class LeadObjectPermissionTests(TestCase):
    def setUp(self):
        self.user = create_user(username="owner-a")
        self.other = create_user(username="owner-b")
        self.own_lead = create_lead(user=self.user, nome="Dono", email="dono@example.com")
        self.other_lead = create_lead(user=self.other, nome="Alheio", email="alheio@example.com")
        self.other_interaction = create_interaction(self.other_lead, nota="Interacao de B")
        self.client.force_login(self.user)

    def test_user_a_cannot_list_user_b_lead(self):
        response = self.client.get(reverse("leads:lead_list"))
        self.assertContains(response, "Dono")
        self.assertNotContains(response, "Alheio")

    def test_user_a_cannot_open_edit_or_delete_user_b_lead(self):
        urls = [
            reverse("leads:lead_detail", args=[self.other_lead.pk]),
            reverse("leads:lead_update", args=[self.other_lead.pk]),
            reverse("leads:lead_delete", args=[self.other_lead.pk]),
        ]
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 404)

    def test_user_a_cannot_post_interaction_to_user_b_lead(self):
        response = self.client.post(reverse("leads:lead_detail", args=[self.other_lead.pk]), {"nota": "Hack"})
        self.assertEqual(response.status_code, 404)
        self.assertFalse(Interaction.objects.filter(nota="Hack").exists())

    def test_user_a_cannot_edit_or_delete_user_b_interaction(self):
        edit = self.client.post(reverse("leads:interaction_update", args=[self.other_interaction.pk]), {"nota": "Hack"})
        delete = self.client.post(reverse("leads:interaction_delete", args=[self.other_interaction.pk]))
        self.assertEqual(edit.status_code, 404)
        self.assertEqual(delete.status_code, 404)
        self.other_interaction.refresh_from_db()
        self.assertEqual(self.other_interaction.nota, "Interacao de B")

    def test_other_user_data_is_not_in_dashboard_or_filters(self):
        dashboard = self.client.get(reverse("leads:dashboard"))
        listing = self.client.get(reverse("leads:lead_list"), {"q": "Alheio"})
        self.assertEqual(dashboard.context["total_leads"], 1)
        self.assertEqual(list(listing.context["leads"]), [])

    def test_missing_and_other_users_lead_both_return_404_for_detail(self):
        missing = self.client.get(reverse("leads:lead_detail", args=[99999]))
        other = self.client.get(reverse("leads:lead_detail", args=[self.other_lead.pk]))
        self.assertEqual(missing.status_code, 404)
        self.assertEqual(other.status_code, 404)

    def test_mass_assignment_does_not_change_owner_or_protected_timestamps(self):
        original_created = self.own_lead.criado_em
        original_updated = self.own_lead.atualizado_em
        payload = lead_payload(
            nome="Seguro",
            email="seguro@example.com",
            agente_responsavel=self.other.pk,
            criado_em="2000-01-01T00:00:00Z",
            atualizado_em="2000-01-01T00:00:00Z",
        )
        self.client.post(reverse("leads:lead_update", args=[self.own_lead.pk]), payload)
        self.own_lead.refresh_from_db()
        self.assertEqual(self.own_lead.agente_responsavel, self.user)
        self.assertEqual(self.own_lead.criado_em, original_created)
        self.assertGreaterEqual(self.own_lead.atualizado_em, original_updated)

    def test_export_leads_does_not_include_user_b_data(self):
        response = self.client.get(reverse("leads:export_leads_csv"))
        content = response.content.decode()
        self.assertIn("Dono", content)
        self.assertNotIn("Alheio", content)
