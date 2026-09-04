from django.db import migrations, models


def populate_interaction_timestamps(apps, schema_editor):
    Interaction = apps.get_model("leads", "Interaction")
    Interaction.objects.filter(criado_em__isnull=True).update(criado_em=models.F("data_interacao"))
    Interaction.objects.filter(atualizado_em__isnull=True).update(atualizado_em=models.F("data_interacao"))


class Migration(migrations.Migration):
    dependencies = [
        ("leads", "0005_domain_constraints_and_indexes"),
    ]

    operations = [
        migrations.AddField(
            model_name="interaction",
            name="tipo",
            field=models.CharField(
                choices=[
                    ("LIGACAO", "Ligacao"),
                    ("EMAIL", "E-mail"),
                    ("REUNIAO", "Reuniao"),
                    ("MENSAGEM", "Mensagem"),
                    ("NOTA", "Nota"),
                ],
                default="NOTA",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="interaction",
            name="data_interacao",
            field=models.DateTimeField(),
        ),
        migrations.AddField(
            model_name="interaction",
            name="criado_em",
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name="interaction",
            name="atualizado_em",
            field=models.DateTimeField(null=True),
        ),
        migrations.RunPython(populate_interaction_timestamps, migrations.RunPython.noop),
    ]
