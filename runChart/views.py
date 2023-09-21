from django.shortcuts import render
from django.http import HttpResponse
from .models import *

def index(request):

    runners = Runner.objects.all()
    runningLaps = RunningLap.objects.all()

    data = "Current Data"
    context = {
        "data":data
    }
    return render(request, 'run/index.html', context)