from django.contrib.messages import get_messages
from django.test import Client, TestCase
from django.urls import reverse

from leads.models import Interaction, Lead
from leads.tests.factories import create_interaction, create_lead, create_user, lead_payload


class LeadListTests(TestCase):
    def setUp(self):
        self.user = create_user(username="list-a")
        self.other = create_user(username="list-b")

    def test_list_requires_authentication(self):
        response = self.client.get(reverse("leads:lead_list"))
        self.assertEqual(response.status_code, 302)

    def test_user_without_leads_gets_empty_list(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("leads:lead_list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["leads"]), [])

    def test_list_shows_only_authenticated_users_leads(self):
        own = create_lead(user=self.user, nome="Meu")
        create_lead(user=self.other, nome="Outro")
        self.client.force_login(self.user)
        response = self.client.get(reverse("leads:lead_list"))
        self.assertContains(response, own.nome)
        self.assertNotContains(response, "Outro")

    def test_list_orders_by_created_descending_current_contract(self):
        old = create_lead(user=self.user, nome="Antigo")
        new = create_lead(user=self.user, nome="Novo")
        self.client.force_login(self.user)
        response = self.client.get(reverse("leads:lead_list"))
        leads = list(response.context["leads"])
        self.assertEqual(leads[0], new)
        self.assertIn(old, leads)

    def test_list_paginate_by_ten(self):
        for index in range(11):
            create_lead(user=self.user, nome=f"Lead {index}", email=f"lead{index}@example.com")
        self.client.force_login(self.user)
        response = self.client.get(reverse("leads:lead_list"))
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["leads"]), 10)


class LeadCreateTests(TestCase):
    def setUp(self):
        self.user = create_user(username="create-a")
        self.other = create_user(username="create-b")

    def test_create_get_requires_authentication(self):
        response = self.client.get(reverse("leads:lead_create"))
        self.assertEqual(response.status_code, 302)

    def test_create_get_authenticated_renders_form(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("leads:lead_create"))
        self.assertEqual(response.status_code, 200)

    def test_valid_create_assigns_authenticated_user_and_redirects(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("leads:lead_create"), lead_payload())
        self.assertRedirects(response, reverse("leads:lead_list"))
        lead = Lead.objects.get(email="novo@example.com")
        self.assertEqual(lead.agente_responsavel, self.user)

    def test_posted_responsible_user_is_ignored(self):
        self.client.force_login(self.user)
        payload = lead_payload(agente_responsavel=self.other.pk)
        self.client.post(reverse("leads:lead_create"), payload)
        lead = Lead.objects.get(email=payload["email"])
        self.assertEqual(lead.agente_responsavel, self.user)

    def test_missing_name_does_not_create_lead(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("leads:lead_create"), lead_payload(nome=""))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Lead.objects.filter(email="novo@example.com").exists())

    def test_missing_surname_is_allowed_current_behavior(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("leads:lead_create"), lead_payload(sobrenome=""))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Lead.objects.filter(email="novo@example.com").exists())

    def test_invalid_email_does_not_create_lead(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("leads:lead_create"), lead_payload(email="invalid"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Lead.objects.count(), 0)

    def test_empty_phone_is_allowed_current_behavior(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("leads:lead_create"), lead_payload(telefone=""))
        self.assertEqual(response.status_code, 302)

    def test_invalid_status_and_priority_are_rejected(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("leads:lead_create"), lead_payload(status="BAD", prioridade="BAD"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Lead.objects.count(), 0)

    def test_overlong_name_is_rejected_by_form(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("leads:lead_create"), lead_payload(nome="x" * 256))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Lead.objects.count(), 0)

    def test_duplicate_email_is_allowed_current_behavior(self):
        create_lead(user=self.user, email="dup@example.com")
        self.client.force_login(self.user)
        response = self.client.post(reverse("leads:lead_create"), lead_payload(email="dup@example.com"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Lead.objects.filter(email="dup@example.com").count(), 2)

    def test_create_with_csrf_enforced_without_token_is_forbidden(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        response = client.post(reverse("leads:lead_create"), lead_payload())
        self.assertEqual(response.status_code, 403)

    def test_create_success_adds_message(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("leads:lead_create"), lead_payload(), follow=True)
        messages = [message.message for message in get_messages(response.wsgi_request)]
        self.assertIn("Lead criado com sucesso!", messages)

    def test_put_renders_form_current_behavior(self):
        self.client.force_login(self.user)
        response = self.client.put(reverse("leads:lead_create"), data=lead_payload())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Lead.objects.count(), 0)


class LeadDetailUpdateDeleteTests(TestCase):
    def setUp(self):
        self.user = create_user(username="crud-a")
        self.other = create_user(username="crud-b")
        self.lead = create_lead(user=self.user, nome="Meu", email="meu@example.com")
        self.other_lead = create_lead(user=self.other, nome="Outro", email="outro@example.com")

    def test_detail_requires_authentication(self):
        response = self.client.get(reverse("leads:lead_detail", args=[self.lead.pk]))
        self.assertEqual(response.status_code, 302)

    def test_detail_shows_own_lead_and_interactions(self):
        interaction = create_interaction(self.lead, nota="Nota propria")
        create_interaction(self.other_lead, nota="Nota alheia")
        self.client.force_login(self.user)
        response = self.client.get(reverse("leads:lead_detail", args=[self.lead.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.lead.nome)
        self.assertContains(response, interaction.nota)
        self.assertNotContains(response, "Nota alheia")

    def test_detail_missing_lead_returns_404(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("leads:lead_detail", args=[99999]))
        self.assertEqual(response.status_code, 404)

    def test_detail_other_users_lead_returns_404(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("leads:lead_detail", args=[self.other_lead.pk]))
        self.assertEqual(response.status_code, 404)

    def test_valid_update_changes_own_lead(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("leads:lead_update", args=[self.lead.pk]),
            lead_payload(nome="Atualizado", email="atualizado@example.com", status="VENDIDO", prioridade="ALTA"),
        )
        self.assertRedirects(response, reverse("leads:lead_list"))
        self.lead.refresh_from_db()
        self.assertEqual(self.lead.nome, "Atualizado")
        self.assertEqual(self.lead.status, "VENDIDO")
        self.assertEqual(self.lead.prioridade, "ALTA")

    def test_invalid_update_does_not_change_data(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("leads:lead_update", args=[self.lead.pk]),
            lead_payload(nome="", email="invalid"),
        )
        self.assertEqual(response.status_code, 200)
        self.lead.refresh_from_db()
        self.assertEqual(self.lead.nome, "Meu")
        self.assertEqual(self.lead.email, "meu@example.com")

    def test_update_ignores_attempt_to_change_responsible_user(self):
        self.client.force_login(self.user)
        payload = lead_payload(email="change-owner@example.com", agente_responsavel=self.other.pk)
        self.client.post(reverse("leads:lead_update", args=[self.lead.pk]), payload)
        self.lead.refresh_from_db()
        self.assertEqual(self.lead.agente_responsavel, self.user)

    def test_update_missing_or_other_user_lead_returns_404(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse("leads:lead_update", args=[99999])).status_code, 404)
        self.assertEqual(self.client.get(reverse("leads:lead_update", args=[self.other_lead.pk])).status_code, 404)

    def test_delete_confirmation_get_current_behavior(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("leads:lead_delete", args=[self.lead.pk]))
        self.assertEqual(response.status_code, 200)

    def test_delete_post_removes_lead_and_interactions(self):
        interaction = create_interaction(self.lead)
        self.client.force_login(self.user)
        response = self.client.post(reverse("leads:lead_delete", args=[self.lead.pk]))
        self.assertRedirects(response, reverse("leads:lead_list"))
        self.assertFalse(Lead.objects.filter(pk=self.lead.pk).exists())
        self.assertFalse(Interaction.objects.filter(pk=interaction.pk).exists())

    def test_delete_missing_or_other_user_lead_returns_404(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.post(reverse("leads:lead_delete", args=[99999])).status_code, 404)
        self.assertEqual(self.client.post(reverse("leads:lead_delete", args=[self.other_lead.pk])).status_code, 404)

    def test_delete_message_is_added(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("leads:lead_delete", args=[self.lead.pk]), follow=True)
        messages = [message.message for message in get_messages(response.wsgi_request)]
        self.assertTrue(any(message.startswith("Lead excl") for message in messages))
