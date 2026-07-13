from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from leads.models import Interaction, Lead
from leads.tests.factories import create_interaction, create_lead, create_user


User = get_user_model()


class LeadModelTest(TestCase):
    def setUp(self):
        self.user = create_user(username="testuser", password="password123")
        self.lead = create_lead(
            user=self.user,
            nome="Elon",
            sobrenome="Musk",
            email="elon@tesla.com",
        )

    def test_lead_string_representation(self):
        expected_value = f"{self.lead.nome} - {self.lead.get_status_display()}"
        self.assertEqual(str(self.lead), expected_value)

    def test_lead_status_default(self):
        lead = Lead.objects.create(nome="Default", email="default@example.com", agente_responsavel=self.user)
        self.assertEqual(lead.status, "NOVO")

    def test_lead_priority_default(self):
        lead = Lead.objects.create(nome="Default", email="priority@example.com", agente_responsavel=self.user)
        self.assertEqual(lead.prioridade, "MEDIA")

    def test_valid_lead_creation_and_user_link(self):
        self.assertEqual(self.lead.agente_responsavel, self.user)
        self.assertEqual(self.user.leads.get(pk=self.lead.pk), self.lead)

    def test_status_and_priority_choices_are_current_contract(self):
        self.assertIn(("NOVO", "Novo"), Lead.STATUS_CHOICES)
        self.assertIn(("ALTA", "Alta"), Lead.PRIORITY_CHOICES)

    def test_timestamps_are_set(self):
        self.assertIsNotNone(self.lead.criado_em)
        self.assertIsNotNone(self.lead.atualizado_em)

    def test_deleting_user_cascades_to_leads(self):
        lead_id = self.lead.id
        self.user.delete()
        self.assertFalse(Lead.objects.filter(id=lead_id).exists())

    def test_responsible_user_can_be_null_currently(self):
        lead = create_lead(user=None, agente_responsavel=None, email="orphan@example.com")
        self.assertIsNone(lead.agente_responsavel)

    def test_model_full_clean_rejects_invalid_email(self):
        lead = create_lead(email="invalid-email")
        with self.assertRaises(ValidationError):
            lead.full_clean()

    def test_database_allows_duplicate_email_currently(self):
        create_lead(user=self.user, email="same@example.com")
        create_lead(user=self.user, email="same@example.com")
        self.assertEqual(Lead.objects.filter(email="same@example.com").count(), 2)

    def test_full_clean_rejects_overlong_name(self):
        lead = create_lead(nome="x" * 256)
        with self.assertRaises(ValidationError):
            lead.full_clean()

    def test_no_default_model_ordering_is_defined(self):
        self.assertEqual(Lead._meta.ordering, [])


class InteractionModelTest(TestCase):
    def setUp(self):
        self.user = create_user(username="interaction-user")
        self.lead = create_lead(user=self.user)

    def test_valid_interaction_creation_and_lead_link(self):
        interaction = create_interaction(self.lead, nota="Ligacao feita")
        self.assertEqual(interaction.lead, self.lead)
        self.assertEqual(self.lead.interactions.get(pk=interaction.pk), interaction)

    def test_interaction_string_representation(self):
        interaction = create_interaction(self.lead, nota="Ligacao feita")
        self.assertIn(self.lead.nome, str(interaction))

    def test_interaction_date_is_set_automatically(self):
        interaction = create_interaction(self.lead)
        self.assertIsNotNone(interaction.data_interacao)

    def test_deleting_lead_cascades_to_interactions(self):
        interaction = create_interaction(self.lead)
        self.lead.delete()
        self.assertFalse(Interaction.objects.filter(pk=interaction.pk).exists())

    def test_note_blank_is_allowed_by_database_but_not_by_model_validation(self):
        interaction = create_interaction(self.lead, nota="")
        self.assertEqual(interaction.nota, "")
        with self.assertRaises(ValidationError):
            interaction.full_clean()

    def test_interaction_requires_lead_at_database_level(self):
        with self.assertRaises(IntegrityError):
            Interaction.objects.create(nota="Sem lead")

    def test_interaction_can_point_to_orphan_lead_currently(self):
        lead = create_lead(user=None, agente_responsavel=None, email="orphan-interaction@example.com")
        interaction = create_interaction(lead)
        self.assertIsNone(interaction.lead.agente_responsavel)

    def test_no_default_interaction_ordering_is_defined(self):
        self.assertEqual(Interaction._meta.ordering, [])
