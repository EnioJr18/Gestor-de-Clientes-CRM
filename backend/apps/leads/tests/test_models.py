from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from apps.leads.models import Interaction, Lead
from apps.leads.tests.factories import create_interaction, create_lead, create_user


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

    def test_responsible_user_is_required_at_database_level(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Lead.objects.create(nome="Orfao", email="orphan@example.com", agente_responsavel=None)

    def test_model_full_clean_rejects_invalid_email(self):
        lead = create_lead(email="invalid-email")
        with self.assertRaises(ValidationError):
            lead.full_clean()

    def test_database_rejects_duplicate_email_for_same_user_case_insensitive(self):
        create_lead(user=self.user, email="same@example.com")
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                create_lead(user=self.user, email="SAME@example.com")

    def test_database_allows_same_email_for_different_users(self):
        other = create_user(username="other-owner")
        create_lead(user=self.user, email="shared@example.com")
        create_lead(user=other, email="shared@example.com")
        self.assertEqual(Lead.objects.filter(email="shared@example.com").count(), 2)

    def test_database_rejects_invalid_status_and_priority(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                create_lead(user=self.user, email="bad-status@example.com", status="BAD")
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                create_lead(user=self.user, email="bad-priority@example.com", prioridade="BAD")

    def test_declares_domain_indexes_and_constraints(self):
        index_names = {index.name for index in Lead._meta.indexes}
        constraint_names = {constraint.name for constraint in Lead._meta.constraints}

        self.assertIn("lead_owner_status_idx", index_names)
        self.assertIn("lead_owner_priority_idx", index_names)
        self.assertIn("lead_owner_created_idx", index_names)
        self.assertIn("lead_owner_email_ci_uniq", constraint_names)
        self.assertIn("lead_status_valid_chk", constraint_names)
        self.assertIn("lead_priority_valid_chk", constraint_names)

    def test_full_clean_rejects_overlong_name(self):
        lead = Lead(
            nome="x" * 256,
            email="overlong@example.com",
            agente_responsavel=self.user,
        )
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

    def test_note_blank_is_rejected_by_database_and_model_validation(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                create_interaction(self.lead, nota="")
        interaction = Interaction(lead=self.lead, nota="")
        with self.assertRaises(ValidationError):
            interaction.full_clean()

    def test_note_with_only_spaces_is_rejected_by_model_validation(self):
        interaction = Interaction(lead=self.lead, nota="   \n\t")
        with self.assertRaises(ValidationError):
            interaction.full_clean()

    def test_invalid_interaction_type_is_rejected_by_database(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                create_interaction(self.lead, tipo="INVALIDO")

    def test_interaction_requires_lead_at_database_level(self):
        with self.assertRaises(IntegrityError):
            Interaction.objects.create(nota="Sem lead")

    def test_no_default_interaction_ordering_is_defined(self):
        self.assertEqual(Interaction._meta.ordering, [])

    def test_declares_interaction_indexes_and_constraints(self):
        index_names = {index.name for index in Interaction._meta.indexes}
        constraint_names = {constraint.name for constraint in Interaction._meta.constraints}

        self.assertIn("inter_lead_date_idx", index_names)
        self.assertIn("interaction_nota_not_empty_chk", constraint_names)
        self.assertIn("interaction_tipo_valid_chk", constraint_names)
