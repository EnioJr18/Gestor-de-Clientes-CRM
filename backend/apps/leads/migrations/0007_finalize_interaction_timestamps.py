from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("leads", "0006_interaction_api_fields"),
    ]

    operations = [
        migrations.AlterField(
            model_name="interaction",
            name="data_interacao",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name="interaction",
            name="criado_em",
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name="interaction",
            name="atualizado_em",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
