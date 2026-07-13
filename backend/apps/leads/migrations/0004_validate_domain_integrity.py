from django.db import migrations


VALID_STATUSES = {"NOVO", "EM_NEGOCIACAO", "PROPOSTA_ENVIADA", "VENDIDO", "PERDIDO"}
VALID_PRIORITIES = {"BAIXA", "MEDIA", "ALTA"}


def validate_domain_integrity(apps, schema_editor):
    Lead = apps.get_model("leads", "Lead")
    Interaction = apps.get_model("leads", "Interaction")

    orphan_lead_ids = list(
        Lead.objects.filter(agente_responsavel__isnull=True).values_list("id", flat=True)[:20]
    )
    if orphan_lead_ids:
        raise RuntimeError(
            "Nao e seguro tornar agente_responsavel obrigatorio: "
            f"existem leads sem responsavel. IDs iniciais: {orphan_lead_ids}"
        )

    empty_name_ids = list(Lead.objects.filter(nome="").values_list("id", flat=True)[:20])
    if empty_name_ids:
        raise RuntimeError(
            "Nao e seguro aplicar constraint de nome obrigatorio: "
            f"existem leads com nome vazio. IDs iniciais: {empty_name_ids}"
        )

    empty_email_ids = list(Lead.objects.filter(email="").values_list("id", flat=True)[:20])
    if empty_email_ids:
        raise RuntimeError(
            "Nao e seguro aplicar constraint de e-mail obrigatorio: "
            f"existem leads com e-mail vazio. IDs iniciais: {empty_email_ids}"
        )

    invalid_status_ids = list(
        Lead.objects.exclude(status__in=VALID_STATUSES).values_list("id", flat=True)[:20]
    )
    if invalid_status_ids:
        raise RuntimeError(
            "Nao e seguro aplicar constraint de status: "
            f"existem leads com status invalido. IDs iniciais: {invalid_status_ids}"
        )

    invalid_priority_ids = list(
        Lead.objects.exclude(prioridade__in=VALID_PRIORITIES).values_list("id", flat=True)[:20]
    )
    if invalid_priority_ids:
        raise RuntimeError(
            "Nao e seguro aplicar constraint de prioridade: "
            f"existem leads com prioridade invalida. IDs iniciais: {invalid_priority_ids}"
        )

    empty_note_ids = list(Interaction.objects.filter(nota="").values_list("id", flat=True)[:20])
    if empty_note_ids:
        raise RuntimeError(
            "Nao e seguro aplicar constraint de nota obrigatoria: "
            f"existem interacoes com nota vazia. IDs iniciais: {empty_note_ids}"
        )

    duplicate_emails = []
    seen = {}
    for lead in Lead.objects.exclude(email="").only("id", "agente_responsavel_id", "email"):
        key = (lead.agente_responsavel_id, lead.email.lower())
        if key in seen:
            duplicate_emails.append((seen[key], lead.id))
            if len(duplicate_emails) >= 20:
                break
        else:
            seen[key] = lead.id
    if duplicate_emails:
        raise RuntimeError(
            "Nao e seguro aplicar unicidade de e-mail por responsavel: "
            f"existem duplicidades. Pares iniciais de IDs: {duplicate_emails}"
        )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("leads", "0003_lead_sobrenome"),
    ]

    operations = [
        migrations.RunPython(validate_domain_integrity, noop_reverse),
    ]
