# Generated by Django 4.2.5 on 2023-09-26 09:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("runChart", "0007_runninglap_endlapdate"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="runninglap",
            name="endLapTime",
        ),
    ]