# Generated by Django 4.1.9 on 2023-09-21 16:48

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("runChart", "0006_runninglap_numberoflaps"),
    ]

    operations = [
        migrations.AddField(
            model_name="runninglap",
            name="endLapDate",
            field=models.DateTimeField(
                default=datetime.datetime(2023, 10, 22, 22, 0),
                verbose_name="Data zakonczenia okrazenia",
            ),
        ),
    ]
