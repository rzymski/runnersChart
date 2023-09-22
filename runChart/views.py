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
    dict = get_laps_for_every_time()
    context = {
        "dict": dict
    }
    return render(request, 'chart/line.html', context)


import pytz
def get_laps_for_every_time():
    running_laps = list(RunningLap.objects.values_list('endLapDate', flat=True).distinct().order_by('endLapDate'))
    europe_warsaw = pytz.timezone('Europe/Warsaw')
    running_laps = [dt.astimezone(europe_warsaw) for dt in running_laps]
    dict = {running_lap: [0] * Runner.objects.count() for running_lap in running_laps}
    runners = Runner.objects.all()
    for endLapDate in dict:
        for runner in runners:
            dict[endLapDate][runner.id-1] = get_max_laps_for_runner_before_date(runner.id, endLapDate)
    return dict

def get_max_laps_for_runner_before_date(runner_id, end_lap_date):
    max_laps = RunningLap.objects.filter(
        runnerId=runner_id,
        endLapDate__lte=end_lap_date
    ).order_by('-numberOfLaps').first()
    if max_laps:
        return max_laps.numberOfLaps
    else:
        return 0
