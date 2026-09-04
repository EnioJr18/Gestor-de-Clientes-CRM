from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("leads", "0007_finalize_interaction_timestamps"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="interaction",
            constraint=models.CheckConstraint(
                condition=models.Q(tipo__in=["LIGACAO", "EMAIL", "REUNIAO", "MENSAGEM", "NOTA"]),
                name="interaction_tipo_valid_chk",
            ),
        ),
    ]
