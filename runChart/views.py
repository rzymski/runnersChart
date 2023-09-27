from django.shortcuts import render
from .models import *
from datetime import datetime, time
import pytz

from .forms import runTimeForm

def resultTable(request):
    return render(request, 'table/result.html')
def customAdmin(request):
    return render(request, 'admin/customAdmin.html')

def xd(request):
    if request.method == "POST":
        form = runTimeForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name_input']
            date = form.cleaned_data['date_input']
            time = form.cleaned_data['time_input']

            print("Name:", name)
            print("Date:", date)
            print("Time:", time)
        else:
            print("Form is not valid")
    form = runTimeForm()
    return render(request, 'chart/xd.html', {'form': form})

def index(request):
    return line_chart(request)

colors = ['rgb(255,51,51)', 'rgb(255,128,0)', 'rgb(255,255,0)', 'rgb(221,160,221)', 'rgb(0,255,0)',
              'rgb(160,82,45)', 'rgb(0,255,255)', 'rgb(0,128,255)', 'rgb(0,0,255)', 'rgb(127,0,255)', 'rgb(255,0,255)',
              'rgb(255,0,127)', 'rgb(128,128,128)', 'rgb(0,0,0)', 'rgb(255,204,204)', 'rgb(255,229,204)',
              'rgb(255,255,204)', 'rgb(229,255,229)', 'rgb(204,255,255)', 'rgb(204,229,255)', 'rgb(204,204,255)',
              'rgb(229,204,255)', 'rgb(255,204,255)', 'rgb(255,204,229)', 'rgb(153,0,0)', 'rgb(153,153,0)',
              'rgb(255,215,0)', 'rgb(255,140,0)', 'rgb(192,192,192)', 'rgb(148,0,211)', ]

def line_chart(request):
    time_strings = [dt.strftime('%H:%M') for dt in list(get_laps_for_every_time())]

    runners = []
    for runner in Runner.objects.all():
        stringRunner = str(runner)
        runners.append(stringRunner)
    #Wersja z posortowanymi biegaczami względem wyników
    #runners = get_best_runners()

    runsData = get_runners_laps_in_time()
    context = {
        'labels': time_strings,
        'runners': runners,
        'colors': colors,
        'runsData': runsData,
    }
    return render(request, 'chart/line.html', context)


def get_best_runners():
    bestRuns = []
    runners = []
    runs = RunningLap.objects.all().order_by('-numberOfLaps').distinct()
    for run in runs:
        if run.runnerId not in bestRuns:
            bestRuns.append(run.runnerId)
            runners.append(run.runnerId.__str__())
    return runners

def get_runners_laps_in_time():
    result = []
    for i in range(Runner.objects.count()):
        result.append([])
    runningLaps = RunningLap.objects.all().order_by('endLapDate')
    warsaw_tz = pytz.timezone('Europe/Warsaw')

    runners = get_best_runners()

    for run in runningLaps:
        if run.runnerId is not None:
            start_lap_date_warsaw = run.startLapDate.astimezone(warsaw_tz)
            result[run.runnerId.id-1].append({'x': time(start_lap_date_warsaw.hour, start_lap_date_warsaw.minute).strftime('%H:%M'), 'y': run.numberOfLaps - 1})
            end_lap_date_warsaw = run.endLapDate.astimezone(warsaw_tz)
            result[run.runnerId.id-1].append({'x': time(end_lap_date_warsaw.hour, end_lap_date_warsaw.minute).strftime('%H:%M'), 'y': run.numberOfLaps})
            # Wersja z posortowanymi biegaczami wzgledem wyników
            # runnerIndex = runners.index(run.runnerId.__str__())
            # start_lap_date_warsaw = run.startLapDate.astimezone(warsaw_tz)
            # result[runnerIndex].append({'x': time(start_lap_date_warsaw.hour, start_lap_date_warsaw.minute).strftime('%H:%M'), 'y': run.numberOfLaps-1})
            # end_lap_date_warsaw = run.endLapDate.astimezone(warsaw_tz)
            # result[runnerIndex].append({'x': time(end_lap_date_warsaw.hour, end_lap_date_warsaw.minute).strftime('%H:%M'), 'y': run.numberOfLaps})
    return result



def get_laps_for_every_time():
    runningLapStartDates = list(RunningLap.objects.values_list('startLapDate', flat=True).distinct().order_by('startLapDate'))
    runningLapEndDates = list(RunningLap.objects.values_list('endLapDate', flat=True).distinct().order_by('endLapDate'))
    runningLapsDates = sorted(runningLapStartDates + runningLapEndDates)
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
