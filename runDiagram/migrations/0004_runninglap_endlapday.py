# Generated by Django 4.1.9 on 2023-09-21 10:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("runDiagram", "0003_alter_runninglap_endlaptime"),
    ]

    operations = [
        migrations.AddField(
            model_name="runninglap",
            name="endLapDay",
            field=models.IntegerField(
                default=0, verbose_name="Dzien zakonczenia okrazenia"
            ),
            preserve_default=False,
        ),
    ]
