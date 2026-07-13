import csv
import io

from django.test import TestCase
from django.urls import reverse

from leads.tests.factories import create_interaction, create_lead, create_user
from leads.views import _sanitize_csv_cell


def rows_from_response(response):
    text = response.content.decode()
    return list(csv.reader(io.StringIO(text)))


class LeadCsvExportTests(TestCase):
    def setUp(self):
        self.user = create_user(username="csv-a")
        self.other = create_user(username="csv-b")

    def test_export_requires_authentication(self):
        response = self.client.get(reverse("leads:export_leads_csv"))
        self.assertEqual(response.status_code, 302)

    def test_export_headers_and_empty_dataset(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("leads:export_leads_csv"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")
        self.assertIn('filename="leads.csv"', response["Content-Disposition"])
        self.assertEqual(rows_from_response(response), [["Nome", "Email", "Telefone", "Status", "Prioridade", "Criado Em"]])

    def test_export_includes_only_authenticated_users_leads(self):
        create_lead(user=self.user, nome="Meu", email="meu@example.com", telefone="")
        create_lead(user=self.other, nome="Outro", email="outro@example.com")
        self.client.force_login(self.user)
        rows = rows_from_response(self.client.get(reverse("leads:export_leads_csv")))
        content = "\n".join(",".join(row) for row in rows)
        self.assertIn("Meu", content)
        self.assertNotIn("Outro", content)

    def test_export_handles_commas_quotes_newlines_and_accents(self):
        create_lead(user=self.user, nome='Maria, "QA"', sobrenome="Teste", email="maria@example.com", telefone="linha\n2")
        self.client.force_login(self.user)
        rows = rows_from_response(self.client.get(reverse("leads:export_leads_csv")))
        self.assertEqual(rows[1][0], 'Maria, "QA"')
        self.assertEqual(rows[1][2], "linha\n2")

    def test_export_order_matches_current_queryset_order(self):
        first = create_lead(user=self.user, nome="Primeiro", email="primeiro@example.com")
        second = create_lead(user=self.user, nome="Segundo", email="segundo@example.com")
        self.client.force_login(self.user)
        rows = rows_from_response(self.client.get(reverse("leads:export_leads_csv")))
        self.assertEqual([rows[1][0], rows[2][0]], [first.nome, second.nome])

    def test_csv_injection_prefixes_dangerous_values(self):
        create_lead(user=self.user, nome="=SUM(1+1)", email="+cmd@example.com", telefone="-10+20")
        create_lead(user=self.user, nome="@formula", email="tab@example.com", telefone="\t=cmd")
        create_lead(user=self.user, nome="\r=cmd", email="cr@example.com", telefone="859")
        self.client.force_login(self.user)
        rows = rows_from_response(self.client.get(reverse("leads:export_leads_csv")))
        flat_values = [value for row in rows[1:] for value in row]
        self.assertIn("'=SUM(1+1)", flat_values)
        self.assertIn("'+cmd@example.com", flat_values)
        self.assertIn("'-10+20", flat_values)
        self.assertIn("'@formula", flat_values)
        self.assertIn("'\t=cmd", flat_values)
        self.assertIn("'\r=cmd", flat_values)

    def test_csv_injection_expected_to_prefix_dangerous_values(self):
        create_lead(user=self.user, nome="@formula", email="safe@example.com", telefone="\t=cmd")
        self.client.force_login(self.user)
        rows = rows_from_response(self.client.get(reverse("leads:export_leads_csv")))
        self.assertTrue(rows[1][0].startswith("'"))
        self.assertTrue(rows[1][2].startswith("'"))

    def test_csv_sanitizer_preserves_safe_values_and_handles_types(self):
        self.assertEqual(_sanitize_csv_cell(None), "")
        self.assertEqual(_sanitize_csv_cell(123), "123")
        self.assertEqual(_sanitize_csv_cell("Maria"), "Maria")
        self.assertEqual(_sanitize_csv_cell("cliente@example.com"), "cliente@example.com")
        self.assertEqual(_sanitize_csv_cell("Observação comum"), "Observação comum")
        self.assertEqual(_sanitize_csv_cell("'=already"), "'=already")


class InteractionCsvExportTests(TestCase):
    def setUp(self):
        self.user = create_user(username="csv-int-a")
        self.other = create_user(username="csv-int-b")
        self.lead = create_lead(user=self.user, nome="Cliente")
        self.other_lead = create_lead(user=self.other, nome="Outro")

    def test_export_interactions_requires_authentication(self):
        response = self.client.get(reverse("leads:export_interactions_csv", args=[self.lead.pk]))
        self.assertEqual(response.status_code, 302)

    def test_export_interactions_for_own_lead(self):
        create_interaction(self.lead, nota="Nota com acento e virgula, ok")
        self.client.force_login(self.user)
        response = self.client.get(reverse("leads:export_interactions_csv", args=[self.lead.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")
        self.assertIn("historico_Cliente.csv", response["Content-Disposition"])
        rows = rows_from_response(response)
        self.assertEqual(rows[0], ["Data", "Nota"])
        self.assertEqual(rows[1][1], "Nota com acento e virgula, ok")

    def test_export_interactions_for_other_user_or_missing_lead_returns_404(self):
        self.client.force_login(self.user)
        other = self.client.get(reverse("leads:export_interactions_csv", args=[self.other_lead.pk]))
        missing = self.client.get(reverse("leads:export_interactions_csv", args=[99999]))
        self.assertEqual(other.status_code, 404)
        self.assertEqual(missing.status_code, 404)

    def test_export_interactions_empty_dataset(self):
        self.client.force_login(self.user)
        rows = rows_from_response(self.client.get(reverse("leads:export_interactions_csv", args=[self.lead.pk])))
        self.assertEqual(rows, [["Data", "Nota"]])

    def test_interaction_csv_injection_prefixes_dangerous_note(self):
        create_interaction(self.lead, nota="@formula")
        self.client.force_login(self.user)
        rows = rows_from_response(self.client.get(reverse("leads:export_interactions_csv", args=[self.lead.pk])))
        self.assertEqual(rows[1][1], "'@formula")

    def test_interaction_csv_injection_expected_to_prefix_dangerous_note(self):
        create_interaction(self.lead, nota="=SUM(1+1)")
        self.client.force_login(self.user)
        rows = rows_from_response(self.client.get(reverse("leads:export_interactions_csv", args=[self.lead.pk])))
        self.assertTrue(rows[1][1].startswith("'"))

    def test_interaction_csv_injection_prefixes_all_dangerous_prefixes(self):
        for note in ["=SUM(1+1)", "+cmd", "-10+20", "@formula", "\t=cmd", "\r=cmd"]:
            create_interaction(self.lead, nota=note)

        self.client.force_login(self.user)
        rows = rows_from_response(self.client.get(reverse("leads:export_interactions_csv", args=[self.lead.pk])))
        exported_notes = [row[1] for row in rows[1:]]
        self.assertIn("'=SUM(1+1)", exported_notes)
        self.assertIn("'+cmd", exported_notes)
        self.assertIn("'-10+20", exported_notes)
        self.assertIn("'@formula", exported_notes)
        self.assertIn("'\t=cmd", exported_notes)
        self.assertIn("'\r=cmd", exported_notes)
