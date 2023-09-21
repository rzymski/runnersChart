# Generated by Django 4.1.9 on 2023-09-21 09:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("runDiagram", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="runninglap",
            name="endLapTime",
            field=models.DateTimeField(verbose_name="Czas zakonczenia okrazenia"),
        ),
        migrations.AlterField(
            model_name="runninglap",
            name="runnerId",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="runDiagram.runner",
                verbose_name="Biegacz",
            ),
        ),
    ]
