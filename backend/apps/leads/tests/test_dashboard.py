from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.leads.tests.factories import create_interaction, create_lead, create_user, set_created_at


class DashboardViewTest(TestCase):
    def test_dashboard_redirects_anonymous_user(self):
        url = reverse("leads:dashboard")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_dashboard_logged_in_user(self):
        user = create_user(username="testdashboard", password="password123")
        self.client.force_login(user)
        url = reverse("leads:dashboard")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "leads/dashboard.html")


class DashboardCharacterizationTests(TestCase):
    def setUp(self):
        self.user = create_user(username="dash-a")
        self.other = create_user(username="dash-b")
        self.client.force_login(self.user)

    def test_dashboard_without_leads_has_zero_totals_and_empty_lists(self):
        response = self.client.get(reverse("leads:dashboard"))
        self.assertEqual(response.context["total_leads"], 0)
        self.assertEqual(response.context["labels_status"], [])
        self.assertEqual(response.context["data_status"], [])
        self.assertEqual(list(response.context["interacoes_recentes"]), [])

    def test_dashboard_counts_only_authenticated_users_leads(self):
        create_lead(user=self.user, status="NOVO", prioridade="ALTA")
        create_lead(user=self.user, status="VENDIDO", prioridade="MEDIA")
        create_lead(user=self.other, status="NOVO", prioridade="ALTA")
        response = self.client.get(reverse("leads:dashboard"))
        self.assertEqual(response.context["total_leads"], 2)
        self.assertEqual(sum(response.context["data_status"]), 2)
        self.assertEqual(sum(response.context["data_prioridade"]), 2)

    def test_dashboard_status_and_priority_labels_match_current_choices(self):
        create_lead(user=self.user, status="NOVO", prioridade="ALTA")
        create_lead(user=self.user, status="PERDIDO", prioridade="BAIXA")
        response = self.client.get(reverse("leads:dashboard"))
        self.assertCountEqual(response.context["labels_status"], ["NOVO", "PERDIDO"])
        self.assertCountEqual(response.context["labels_prioridade"], ["ALTA", "BAIXA"])

    def test_dashboard_recent_interactions_are_limited_and_isolated(self):
        own_lead = create_lead(user=self.user)
        other_lead = create_lead(user=self.other)
        for index in range(6):
            create_interaction(own_lead, nota=f"Own {index}")
        create_interaction(other_lead, nota="Other")
        response = self.client.get(reverse("leads:dashboard"))
        notes = [interaction.nota for interaction in response.context["interacoes_recentes"]]
        self.assertEqual(len(notes), 5)
        self.assertNotIn("Other", notes)

    def test_dashboard_counts_new_leads_today(self):
        today = set_created_at(create_lead(user=self.user), timezone.now())
        response = self.client.get(reverse("leads:dashboard"))
        self.assertContains(response, "Novos Hoje")
        self.assertIn('<h3 class="card-value">1</h3>', response.content.decode())
        self.assertEqual(response.context["novos_hoje"], 1)
        self.assertEqual(today.agente_responsavel, self.user)

    def test_dashboard_ignores_yesterday_and_other_users_new_leads_today(self):
        set_created_at(create_lead(user=self.user), timezone.now())
        set_created_at(create_lead(user=self.user), timezone.now() - timedelta(days=1))
        set_created_at(create_lead(user=self.other), timezone.now())
        response = self.client.get(reverse("leads:dashboard"))
        self.assertEqual(response.context["novos_hoje"], 1)
        self.assertIn('<h3 class="card-value">1</h3>', response.content.decode())

    def test_dashboard_counts_multiple_new_leads_today_and_zero_for_empty_user(self):
        set_created_at(create_lead(user=self.user), timezone.now())
        set_created_at(create_lead(user=self.user), timezone.now())
        response = self.client.get(reverse("leads:dashboard"))
        self.assertEqual(response.context["novos_hoje"], 2)

        empty_user = create_user(username="dash-empty")
        self.client.force_login(empty_user)
        empty_response = self.client.get(reverse("leads:dashboard"))
        self.assertEqual(empty_response.context["novos_hoje"], 0)

    def test_chart_context_handles_special_characters_without_other_users_data(self):
        create_lead(user=self.user, nome="Cliente 'Especial'", status="NOVO", prioridade="MEDIA")
        create_lead(user=self.other, nome="Outro", status="PERDIDO", prioridade="ALTA")
        response = self.client.get(reverse("leads:dashboard"))
        self.assertEqual(response.context["labels_status"], ["NOVO"])
        self.assertEqual(response.context["labels_prioridade"], ["MEDIA"])
