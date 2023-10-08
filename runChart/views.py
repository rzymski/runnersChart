from django.shortcuts import render, redirect
from .models import *
from .functions import *
from datetime import datetime, time, timedelta
import pytz
from .forms import *

def runnerResults(request, runnerId):
    runner = Runner.objects.get(id=runnerId)
    runs = RunningLap.objects.exclude(endLapDate=None).filter(runnerId=runner)
    results = []
    for run in runs:
        rank = get_actual_ranking(run)
        startDate = run.startLapDate + timedelta(hours=2)
        endDate = run.endLapDate + timedelta(hours=2)
        results.append([run.numberOfLaps, startDate.strftime('%H:%M'), endDate.strftime('%H:%M'), rank])
    return render(request, 'table/runnerResults.html', {'runner': runner, 'runs': results, "table_script": 'tableRunnerResults'})

def customAdmin(request):
    lastRunsData = get_runner_actual_laps_and_status()
    for index, lastRun in enumerate(lastRunsData, 1):
        lastRun.append(timeForm(prefix=str(index)))
    mainTime = MyTimeForm(prefix='mainTimeForm')
    if request.method == 'POST':
        if 'singleInputSubmit' in request.POST:
            # print("Single input work")
            for formInList in [sublist[6] for sublist in lastRunsData]:
                if f"{formInList.prefix}-start_time_input" in request.POST and f"{formInList.prefix}-end_time_input" in request.POST:
                    form = timeForm(request.POST, prefix=formInList.prefix)
                    if form.is_valid():
                        startTime = form.cleaned_data['start_time_input']
                        endTime = form.cleaned_data['end_time_input']
                        errorInformation = try_save_runningLap(form.prefix, startTime, endTime)
                        print(errorInformation) if errorInformation is not None else print("BRAK BLEDOW")
                    else:
                        print("NOT VALID")
        elif 'checkBoxSubmit' in request.POST and 'mainTimeForm-time_input' in request.POST:
            # print("Checkbox work")
            selected_items = request.POST.getlist('selected_items')
            mainTimeData = request.POST.get('mainTimeForm-time_input')
            errorInformation = save_multiple_runningLaps(selected_items, mainTimeData)
            print(errorInformation) if errorInformation is not None else print("BRAK BLEDOW")
        return redirect('customAdmin')
    return render(request, 'admin/customAdmin.html', {"lastRunsData": lastRunsData, "table_script": 'tableAdmin', 'mainTime': mainTime})

def resultTable(request):
    runsData = get_runner_laps_and_records()
    return render(request, 'table/result.html', {"runsData": runsData, "table_script": 'tableUser'})
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
    # Wersja z posortowanymi biegaczami względem wyników
    # runners = get_best_runners()

    runsData = get_runners_laps_in_time()
    context = {
        'labels': time_strings,
        'runners': runners,
        'colors': colors,
        'runsData': runsData,
    }
    return render(request, 'chart/line.html', context)
