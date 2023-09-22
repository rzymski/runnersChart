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
    time_strings = [dt.strftime('%H:%M') for dt in list(get_laps_for_every_time())]
    runners = []
    for runner in Runner.objects.all():
        stringRunner = str(runner)
        runners.append(stringRunner)
    laps = get_laps_for_every_runner()
    colors = ['rgb(255,51,51)','rgb(255,128,0)','rgb(255,255,0)','rgb(221,160,221)','rgb(0,255,0)','rgb(160,82,45)','rgb(0,255,255)','rgb(0,128,255)','rgb(0,0,255)','rgb(127,0,255)','rgb(255,0,255)','rgb(255,0,127)','rgb(128,128,128)','rgb(0,0,0)','rgb(255,204,204)','rgb(255,229,204)','rgb(255,255,204)','rgb(229,255,229)','rgb(204,255,255)','rgb(204,229,255)','rgb(204,204,255)','rgb(229,204,255)','rgb(255,204,255)','rgb(255,204,229)','rgb(153,0,0)','rgb(153,153,0)','rgb(255,215,0)','rgb(255,140,0)','rgb(192,192,192)','rgb(148,0,211)',]
    context = {
        'labels': time_strings,
        'runners': runners,
        'laps': laps,
        'colors': colors,
    }
    return render(request, 'chart/line.html', context)


def get_laps_for_every_runner():
    dict = get_laps_for_every_time()
    laps = []
    for i in range(Runner.objects.count()):
        laps.append([])
        for d in dict:
            laps[i].append(dict[d][i])
    return laps

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
