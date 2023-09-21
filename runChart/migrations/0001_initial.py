# Generated by Django 4.1.9 on 2023-09-20 15:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Runner",
            fields=[
                ("id", models.IntegerField(primary_key=True, serialize=False)),
                (
                    "name",
                    models.CharField(max_length=100, verbose_name="Imie biegacza"),
                ),
                (
                    "surname",
                    models.CharField(max_length=100, verbose_name="Nazwisko biegacza"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="RunningLap",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "endLapTime",
                    models.TimeField(verbose_name="Czas zakonczenia okrazenia"),
                ),
                (
                    "runnerId",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="runChart.runner",
                        verbose_name="Id biegacza",
                    ),
                ),
            ],
        ),
    ]