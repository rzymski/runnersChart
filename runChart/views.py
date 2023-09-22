from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import *
from .forms import RunningLapForm

def index(request):
    runningLaps = RunningLap.objects.all()

    if request.method == 'POST':
        form = RunningLapForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = RunningLapForm()

    context = {
        "runningLaps": runningLaps,
        "form":form
    }
    # return render(request, 'chart/index.html', context)
    return render(request, 'chart/line.html', context)

def bar_chart(request):
    runningLaps = RunningLap.objects.all()
    context = {
        "runningLaps": runningLaps
    }
    return render(request, 'chart/bar.html', context)

def line_chart(request):
    runningLaps = RunningLap.objects.all()
    context = {
        "runningLaps": runningLaps
    }
    return render(request, 'chart/line.html', context)