# Generated by Django 4.2.5 on 2023-09-27 22:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("runChart", "0011_endLapDateBlank"),
    ]

    operations = [
        migrations.AlterField(
            model_name="runninglap",
            name="endLapDate",
            field=models.DateTimeField(
                blank=True, null=True, verbose_name="Data zakonczenia okrazenia"
            ),
        ),
    ]
