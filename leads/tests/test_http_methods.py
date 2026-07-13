from django.test import TestCase
from django.urls import reverse

from leads.tests.factories import create_interaction, create_lead, create_user, lead_payload


class HttpMethodCharacterizationTests(TestCase):
    def setUp(self):
        self.user = create_user(username="method-a")
        self.lead = create_lead(user=self.user)
        self.interaction = create_interaction(self.lead)
        self.client.force_login(self.user)

    def test_post_on_read_only_list_currently_allowed_by_listview_as_405(self):
        response = self.client.post(reverse("leads:lead_list"))
        self.assertEqual(response.status_code, 405)

    def test_post_on_dashboard_is_allowed_as_read_view_current_behavior(self):
        response = self.client.post(reverse("leads:dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_put_patch_delete_on_traditional_views_current_behavior(self):
        urls = [
            reverse("leads:lead_create"),
            reverse("leads:lead_update", args=[self.lead.pk]),
            reverse("leads:lead_detail", args=[self.lead.pk]),
        ]
        for url in urls:
            with self.subTest(url=url):
                self.assertIn(self.client.put(url, data=lead_payload()).status_code, [200, 405, 403])
                self.assertIn(self.client.patch(url, data=lead_payload()).status_code, [200, 405, 403])
                self.assertIn(self.client.delete(url).status_code, [200, 405, 403])

    def test_get_on_interaction_delete_redirects_current_behavior(self):
        response = self.client.get(reverse("leads:interaction_delete", args=[self.interaction.pk]))
        self.assertEqual(response.status_code, 302)

    def test_options_returns_a_response_for_class_based_views(self):
        response = self.client.options(reverse("leads:lead_create"))
        self.assertEqual(response.status_code, 200)
