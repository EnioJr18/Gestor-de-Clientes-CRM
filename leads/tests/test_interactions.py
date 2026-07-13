from django.test import Client, TestCase
from django.urls import reverse

from leads.models import Interaction
from leads.tests.factories import create_interaction, create_lead, create_user


class InteractionViewTests(TestCase):
    def setUp(self):
        self.user = create_user(username="inter-a")
        self.other = create_user(username="inter-b")
        self.lead = create_lead(user=self.user, nome="Lead A")
        self.other_lead = create_lead(user=self.other, nome="Lead B")

    def test_create_interaction_requires_authentication(self):
        response = self.client.post(reverse("leads:lead_detail", args=[self.lead.pk]), {"nota": "Teste"})
        self.assertEqual(response.status_code, 302)

    def test_create_valid_interaction_for_own_lead(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("leads:lead_detail", args=[self.lead.pk]), {"nota": "Primeiro contato"})
        self.assertRedirects(response, reverse("leads:lead_detail", args=[self.lead.pk]))
        self.assertTrue(Interaction.objects.filter(lead=self.lead, nota="Primeiro contato").exists())

    def test_create_interaction_for_missing_or_other_user_lead_returns_404(self):
        self.client.force_login(self.user)
        missing = self.client.post(reverse("leads:lead_detail", args=[99999]), {"nota": "Nota"})
        other = self.client.post(reverse("leads:lead_detail", args=[self.other_lead.pk]), {"nota": "Nota"})
        self.assertEqual(missing.status_code, 404)
        self.assertEqual(other.status_code, 404)

    def test_empty_or_spaces_note_is_rejected_by_form(self):
        self.client.force_login(self.user)
        empty = self.client.post(reverse("leads:lead_detail", args=[self.lead.pk]), {"nota": ""})
        spaces = self.client.post(reverse("leads:lead_detail", args=[self.lead.pk]), {"nota": "   "})
        self.assertEqual(empty.status_code, 200)
        self.assertEqual(spaces.status_code, 200)
        self.assertEqual(Interaction.objects.count(), 0)

    def test_long_unicode_note_is_saved(self):
        self.client.force_login(self.user)
        note = "Contato com acentos e emoji :) " + ("x" * 2000)
        response = self.client.post(reverse("leads:lead_detail", args=[self.lead.pk]), {"nota": note})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Interaction.objects.get().nota, note)

    def test_interaction_appears_in_detail_and_ordered_newest_first(self):
        first = create_interaction(self.lead, nota="Primeira")
        second = create_interaction(self.lead, nota="Segunda")
        self.client.force_login(self.user)
        response = self.client.get(reverse("leads:lead_detail", args=[self.lead.pk]))
        interactions = list(response.context["interacoes"])
        self.assertEqual(interactions[0], second)
        self.assertIn(first, interactions)

    def test_update_interaction_for_own_lead(self):
        interaction = create_interaction(self.lead, nota="Antiga")
        self.client.force_login(self.user)
        response = self.client.post(reverse("leads:interaction_update", args=[interaction.pk]), {"nota": "Nova"})
        self.assertRedirects(response, reverse("leads:lead_detail", args=[self.lead.pk]))
        interaction.refresh_from_db()
        self.assertEqual(interaction.nota, "Nova")

    def test_delete_interaction_for_own_lead(self):
        interaction = create_interaction(self.lead)
        self.client.force_login(self.user)
        response = self.client.post(reverse("leads:interaction_delete", args=[interaction.pk]))
        self.assertRedirects(response, reverse("leads:lead_detail", args=[self.lead.pk]))
        self.assertFalse(Interaction.objects.filter(pk=interaction.pk).exists())

    def test_get_delete_redirects_without_deleting_current_behavior(self):
        interaction = create_interaction(self.lead)
        self.client.force_login(self.user)
        response = self.client.get(reverse("leads:interaction_delete", args=[interaction.pk]))
        self.assertRedirects(response, reverse("leads:lead_detail", args=[self.lead.pk]))
        self.assertTrue(Interaction.objects.filter(pk=interaction.pk).exists())

    def test_csrf_required_for_interaction_create(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        response = client.post(reverse("leads:lead_detail", args=[self.lead.pk]), {"nota": "CSRF"})
        self.assertEqual(response.status_code, 403)
