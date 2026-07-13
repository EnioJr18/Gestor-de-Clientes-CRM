import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from django.db.models.functions import Lower


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("leads", "0004_validate_domain_integrity"),
    ]

    operations = [
        migrations.AlterField(
            model_name="lead",
            name="agente_responsavel",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="leads",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="lead",
            name="status",
            field=models.CharField(
                choices=[
                    ("NOVO", "Novo"),
                    ("EM_NEGOCIACAO", "Em Negocia\u00e7\u00e3o"),
                    ("PROPOSTA_ENVIADA", "Proposta Enviada"),
                    ("VENDIDO", "Vendido"),
                    ("PERDIDO", "Perdido"),
                ],
                default="NOVO",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="lead",
            name="prioridade",
            field=models.CharField(
                choices=[("BAIXA", "Baixa"), ("MEDIA", "M\u00e9dia"), ("ALTA", "Alta")],
                default="MEDIA",
                max_length=10,
            ),
        ),
        migrations.AlterField(
            model_name="interaction",
            name="nota",
            field=models.TextField(verbose_name="Anota\u00e7\u00f5es"),
        ),
        migrations.AddConstraint(
            model_name="lead",
            constraint=models.UniqueConstraint(
                "agente_responsavel",
                Lower("email"),
                name="lead_owner_email_ci_uniq",
            ),
        ),
        migrations.AddConstraint(
            model_name="lead",
            constraint=models.CheckConstraint(
                condition=models.Q(status__in=["NOVO", "EM_NEGOCIACAO", "PROPOSTA_ENVIADA", "VENDIDO", "PERDIDO"]),
                name="lead_status_valid_chk",
            ),
        ),
        migrations.AddConstraint(
            model_name="lead",
            constraint=models.CheckConstraint(
                condition=models.Q(prioridade__in=["BAIXA", "MEDIA", "ALTA"]),
                name="lead_priority_valid_chk",
            ),
        ),
        migrations.AddConstraint(
            model_name="lead",
            constraint=models.CheckConstraint(
                condition=~models.Q(nome=""),
                name="lead_nome_not_empty_chk",
            ),
        ),
        migrations.AddConstraint(
            model_name="lead",
            constraint=models.CheckConstraint(
                condition=~models.Q(email=""),
                name="lead_email_not_empty_chk",
            ),
        ),
        migrations.AddConstraint(
            model_name="interaction",
            constraint=models.CheckConstraint(
                condition=~models.Q(nota=""),
                name="interaction_nota_not_empty_chk",
            ),
        ),
        migrations.AddIndex(
            model_name="lead",
            index=models.Index(fields=["agente_responsavel", "status"], name="lead_owner_status_idx"),
        ),
        migrations.AddIndex(
            model_name="lead",
            index=models.Index(fields=["agente_responsavel", "prioridade"], name="lead_owner_priority_idx"),
        ),
        migrations.AddIndex(
            model_name="lead",
            index=models.Index(fields=["agente_responsavel", "-criado_em"], name="lead_owner_created_idx"),
        ),
        migrations.AddIndex(
            model_name="interaction",
            index=models.Index(fields=["lead", "-data_interacao"], name="inter_lead_date_idx"),
        ),
    ]
