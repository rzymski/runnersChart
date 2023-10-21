from django.db import models
from datetime import datetime

class Runner(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, verbose_name="Imie biegacza")
    surname = models.CharField(max_length=100, verbose_name="Nazwisko biegacza")
    finished = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.id} {self.name} {self.surname}"

class RunningLap(models.Model):
    runnerId = models.ForeignKey(Runner, on_delete=models.CASCADE, verbose_name="Biegacz")
    startLapDate = models.DateTimeField(default=datetime(2023, 10, 21, 21, 30), verbose_name="Data rozpoczecia okrazenia")
    endLapDate = models.DateTimeField(verbose_name="Data zakonczenia okrazenia", blank=True, null=True)
    numberOfLaps = models.IntegerField(default=0, verbose_name='Liczba okrazen')
    def __str__(self):
        endTime = self.endLapDate.strftime('%H:%M') if self.endLapDate is not None else 'kiedys'
        return f"{self.runnerId} lap={self.numberOfLaps} st={self.startLapDate.strftime('%H:%M')} end={endTime}"
