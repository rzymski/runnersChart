from django.db import models
from datetime import datetime

class Runner(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, verbose_name="Imie biegacza")
    surname = models.CharField(max_length=100, verbose_name="Nazwisko biegacza")
    def __str__(self):
        return f"{self.id} {self.name} {self.surname}"

class RunningLap(models.Model):
    runnerId = models.ForeignKey(Runner, on_delete=models.CASCADE, verbose_name="Biegacz", null=True)
    endLapTime = models.TimeField(verbose_name="Czas zakonczenia okrazenia")
    endLapDate = models.DateTimeField(default=datetime(2023, 10, 22, 22, 0), verbose_name="Data zakonczenia okrazenia")
    numberOfLaps = models.IntegerField(default=0, verbose_name='Liczba okrazen')
    def __str__(self):
        return f"{self.runnerId} {self.endLapTime}"
