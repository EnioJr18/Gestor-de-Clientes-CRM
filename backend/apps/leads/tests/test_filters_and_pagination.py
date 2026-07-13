from django.core.paginator import PageNotAnInteger
from django.test import RequestFactory, TestCase
from django.urls import reverse

from apps.leads.models import Lead
from apps.leads.tests.factories import create_interaction, create_lead, create_user
from apps.leads.views import leads_by_priority


class SearchFilterTests(TestCase):
    def setUp(self):
        self.user = create_user(username="filter-a")
        self.other = create_user(username="filter-b")
        create_lead(user=self.user, nome="Maria Clara", sobrenome="Silva", email="maria@example.com")
        create_lead(user=self.user, nome="Joao", sobrenome="Souza", email="joao@example.com")
        create_lead(user=self.other, nome="Maria Alheia", email="maria-outro@example.com")
        self.client.force_login(self.user)

    def test_search_by_name_fragment_is_case_insensitive(self):
        response = self.client.get(reverse("leads:lead_list"), {"q": "maria"})
        self.assertContains(response, "Maria Clara")
        self.assertNotContains(response, "Joao")

    def test_empty_search_returns_user_leads(self):
        response = self.client.get(reverse("leads:lead_list"), {"q": ""})
        self.assertContains(response, "Maria Clara")
        self.assertContains(response, "Joao")

    def test_search_without_results(self):
        response = self.client.get(reverse("leads:lead_list"), {"q": "zzz"})
        self.assertNotContains(response, "Maria Clara")
        self.assertEqual(list(response.context["leads"]), [])

    def test_search_does_not_search_email_or_surname_current_behavior(self):
        by_email = self.client.get(reverse("leads:lead_list"), {"q": "joao@example.com"})
        by_surname = self.client.get(reverse("leads:lead_list"), {"q": "Silva"})
        self.assertEqual(list(by_email.context["leads"]), [])
        self.assertEqual(list(by_surname.context["leads"]), [])

    def test_search_never_returns_other_users_lead(self):
        response = self.client.get(reverse("leads:lead_list"), {"q": "Alheia"})
        self.assertNotContains(response, "Maria Alheia")


class ShortcutFilterTests(TestCase):
    def setUp(self):
        self.user = create_user(username="shortcut-a")
        self.other = create_user(username="shortcut-b")
        self.high = create_lead(user=self.user, nome="Alta", prioridade="ALTA", email="alta@example.com")
        self.low = create_lead(user=self.user, nome="Baixa", prioridade="BAIXA", email="baixa@example.com")
        self.other_high = create_lead(user=self.other, nome="Alta Outro", prioridade="ALTA", email="alta-outro@example.com")
        self.client.force_login(self.user)

    def test_recent_leads_returns_latest_ten_for_user(self):
        response = self.client.get(reverse("leads:recent_leads"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Alta Outro")

    def test_leads_without_interactions(self):
        create_interaction(self.high)
        response = self.client.get(reverse("leads:leads_without_interactions"))
        self.assertNotContains(response, "Alta")
        self.assertContains(response, "Baixa")

    def test_high_priority_route_returns_uppercase_alta(self):
        response = self.client.get(reverse("leads:high_priority_leads"))
        self.assertIn(self.high, list(response.context["leads"]))
        self.assertNotIn(self.low, list(response.context["leads"]))
        self.assertNotIn(self.other_high, list(response.context["leads"]))

    def test_priority_filter_accepts_all_valid_choice_values(self):
        factory = RequestFactory()

        for prioridade, _label in Lead.PRIORITY_CHOICES:
            create_lead(
                user=self.user,
                nome=f"Lead {prioridade}",
                prioridade=prioridade,
                email=f"{prioridade.lower()}@example.com",
            )
            request = factory.get(f"/prioridade/{prioridade}/")
            request.user = self.user
            response = leads_by_priority(request, prioridade)
            self.assertContains(response, f"Lead {prioridade}")

    def test_priority_filter_invalid_value_returns_empty_list(self):
        factory = RequestFactory()
        request = factory.get("/prioridade/invalida/")
        request.user = self.user
        response = leads_by_priority(request, "INVALIDA")
        self.assertNotContains(response, "Alta")
        self.assertNotContains(response, "Baixa")


class PaginationTests(TestCase):
    def setUp(self):
        self.user = create_user(username="page-a")
        self.other = create_user(username="page-b")
        for index in range(25):
            create_lead(user=self.user, nome=f"Lead {index:02d}", email=f"page{index}@example.com")
        for index in range(3):
            create_lead(user=self.other, nome=f"Outro {index}", email=f"other-page{index}@example.com")
        self.client.force_login(self.user)

    def test_first_second_and_last_pages(self):
        first = self.client.get(reverse("leads:lead_list"))
        second = self.client.get(reverse("leads:lead_list"), {"page": "2"})
        last = self.client.get(reverse("leads:lead_list"), {"page": "3"})
        self.assertEqual(len(first.context["leads"]), 10)
        self.assertEqual(len(second.context["leads"]), 10)
        self.assertEqual(len(last.context["leads"]), 5)

    def test_invalid_pages_return_404_or_not_integer_behavior(self):
        missing = self.client.get(reverse("leads:lead_list"), {"page": "999"})
        zero = self.client.get(reverse("leads:lead_list"), {"page": "0"})
        negative = self.client.get(reverse("leads:lead_list"), {"page": "-1"})
        self.assertEqual(missing.status_code, 404)
        self.assertEqual(zero.status_code, 404)
        self.assertEqual(negative.status_code, 404)

    def test_text_page_returns_404_current_behavior(self):
        response = self.client.get(reverse("leads:lead_list"), {"page": "abc"})
        self.assertEqual(response.status_code, 404)

    def test_query_string_preserves_search_on_pagination_links(self):
        response = self.client.get(reverse("leads:lead_list"), {"q": "Lead", "page": "2"})
        self.assertContains(response, "q=Lead")

    def test_pagination_is_isolated_by_user(self):
        response = self.client.get(reverse("leads:lead_list"))
        self.assertEqual(response.context["paginator"].count, 25)
