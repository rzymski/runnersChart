from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import *
from .forms import RunningLapForm
from datetime import datetime, timezone


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
        "form": form
    }
    # return render(request, 'chart/index.html', context)
    return line_chart(request)

colors = ['rgb(255,51,51)', 'rgb(255,128,0)', 'rgb(255,255,0)', 'rgb(221,160,221)', 'rgb(0,255,0)',
              'rgb(160,82,45)', 'rgb(0,255,255)', 'rgb(0,128,255)', 'rgb(0,0,255)', 'rgb(127,0,255)', 'rgb(255,0,255)',
              'rgb(255,0,127)', 'rgb(128,128,128)', 'rgb(0,0,0)', 'rgb(255,204,204)', 'rgb(255,229,204)',
              'rgb(255,255,204)', 'rgb(229,255,229)', 'rgb(204,255,255)', 'rgb(204,229,255)', 'rgb(204,204,255)',
              'rgb(229,204,255)', 'rgb(255,204,255)', 'rgb(255,204,229)', 'rgb(153,0,0)', 'rgb(153,153,0)',
              'rgb(255,215,0)', 'rgb(255,140,0)', 'rgb(192,192,192)', 'rgb(148,0,211)', ]

def bar_chart(request):
    time_strings = [dt.strftime('%H:%M') for dt in list(get_laps_for_every_time())]
    runners = []
    for runner in Runner.objects.all():
        stringRunner = str(runner)
        runners.append(stringRunner)
    laps = get_laps_for_every_runner_transpose_matrix()
    print(laps)

    context = {
        'labelTimes': time_strings,
        'lapsInEveryTime': laps,
        'runners': runners,
        'colors': colors,
    }
    return render(request, 'chart/bar.html', context)

def get_laps_for_every_runner_transpose_matrix():
    result = []
    runners = Runner.objects.all()
    for runner in runners:
        laps = RunningLap.objects.filter(runnerId=runner).order_by('endLapDate')
        lapsNumbersList = []
        for lap in laps:
            lapsNumbersList.append(lap.endLapTime.__str__())
        result.append(lapsNumbersList)

    # x = result[0][0]
    # print(type(x))
    # x2 = x.replace(hour=18, minute=0)

    #kwadratowa macierz
    max_length = max(len(inner_list) for inner_list in result)
    square_matrix = [['18:00'] * max_length for _ in range(max_length)]
    for i in range(len(result)):
        for j in range(len(result[i])):
            square_matrix[i][j] = result[i][j]
    #transpozycja macierzy
    max_length = max(len(inner_list) for inner_list in square_matrix)
    transposed = [[] for _ in range(max_length)]
    for inner_list in square_matrix:
        for i, value in enumerate(inner_list):
            transposed[i].append(value)
    print(transposed)
    return transposed

def line_chart(request):
    time_strings = [dt.strftime('%H:%M') for dt in list(get_laps_for_every_time())]
    runners = []
    for runner in Runner.objects.all():
        stringRunner = str(runner)
        runners.append(stringRunner)
    runsData = get_runners_laps_in_time()
    context = {
        'labels': time_strings,
        'runners': runners,
        'colors': colors,
        'runsData': runsData,
    }
    return render(request, 'chart/line.html', context)


def get_runners_laps_in_time():
    result = []
    for i in range(Runner.objects.count()):
        result.append([])
    runningLaps = RunningLap.objects.all()

    for runner in Runner.objects.all():
        result[runner.id - 1].append({'x': '18:00', 'y': 0})

    for run in runningLaps:
        if run.runnerId != None:
            result[run.runnerId.id - 1].append({'x': run.endLapTime.strftime('%H:%M'), 'y': run.numberOfLaps})
    return result


import pytz
def get_laps_for_every_time():
    runningLapsDates = list(RunningLap.objects.values_list('endLapDate', flat=True).distinct().order_by('endLapDate'))
    new_datetime = datetime(2023, 10, 21, 18, 0)
    runningLapsDates.insert(0, new_datetime)
    europe_warsaw = pytz.timezone('Europe/Warsaw')
    running_laps = [dt.astimezone(europe_warsaw) for dt in runningLapsDates]
    dict = {running_lap: [0] * Runner.objects.count() for running_lap in running_laps}
    runners = Runner.objects.all()
    for endLapDate in dict:
        for runner in runners:
            dict[endLapDate][runner.id - 1] = get_max_laps_for_runner_before_date(runner.id, endLapDate)
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
