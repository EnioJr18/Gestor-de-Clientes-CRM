from django.contrib.auth import get_user_model
from django.utils import timezone

from leads.models import Interaction, Lead


User = get_user_model()


def create_user(username="user", password="password123", **kwargs):
    defaults = {
        "email": f"{username}@example.com",
        "first_name": "Test",
        "last_name": "User",
    }
    defaults.update(kwargs)
    return User.objects.create_user(username=username, password=password, **defaults)


def create_lead(user=None, **kwargs):
    if user is None:
        user = create_user(username=f"user{User.objects.count() + 1}")
    defaults = {
        "nome": "Maria",
        "sobrenome": "Silva",
        "email": f"maria{Lead.objects.count() + 1}@example.com",
        "telefone": "85999999999",
        "status": "NOVO",
        "prioridade": "MEDIA",
        "agente_responsavel": user,
    }
    defaults.update(kwargs)
    return Lead.objects.create(**defaults)


def create_interaction(lead=None, **kwargs):
    if lead is None:
        lead = create_lead()
    defaults = {
        "lead": lead,
        "nota": "Contato inicial",
    }
    defaults.update(kwargs)
    return Interaction.objects.create(**defaults)


def set_created_at(obj, value):
    obj.__class__.objects.filter(pk=obj.pk).update(criado_em=value)
    obj.refresh_from_db()
    return obj


def set_interaction_date(obj, value=None):
    if value is None:
        value = timezone.now()
    Interaction.objects.filter(pk=obj.pk).update(data_interacao=value)
    obj.refresh_from_db()
    return obj


def lead_payload(**overrides):
    payload = {
        "nome": "Novo",
        "sobrenome": "Lead",
        "email": "novo@example.com",
        "telefone": "85999999999",
        "status": "NOVO",
        "prioridade": "MEDIA",
    }
    payload.update(overrides)
    return payload
