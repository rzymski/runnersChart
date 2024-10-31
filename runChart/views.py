from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from .models import *
from .functions import *
from datetime import datetime, time, timedelta
import pytz
from .forms import *

from django.contrib.auth.models import auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def loginUser(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            print("OK ZALOGOWAL SIE")
            if 'next' in request.POST:
                return redirect(request.POST['next'])
            return redirect('index')
        else:
            print("OK NIE ZALOGOWAL SIE")
            messages.success(request, 'Invalid Username or Password')
            return redirect('loginUser')
    else:
        print("GET login")
        return render(request, "authenticate/login.html")

def logout(request):
    auth.logout(request)
    return redirect('index')

def runnerResults(request, runnerId):
    runner = Runner.objects.get(id=runnerId)
    runs = RunningLap.objects.exclude(endLapDate=None).filter(runnerId=runner)
    results = []
    for run in runs:
        rank = get_actual_ranking(run)
        startDate = run.startLapDate + timedelta(hours=2)
        endDate = run.endLapDate + timedelta(hours=2)
        timeDelta = endDate - startDate
        results.append([run.numberOfLaps, startDate.strftime('%H:%M'), endDate.strftime('%H:%M'), timeDelta, rank])
    return render(request, 'table/runnerResults.html', {'runner': runner, 'runs': results, "table_script": 'tableRunnerResults'})


@login_required(login_url="loginUser")
def customAdmin(request):
    lastRunsData = get_runner_actual_laps_and_status()
    for index, lastRun in enumerate(lastRunsData, 1):
        lastRun.append(TimeForm(prefix=str(lastRun[0])))
    mainTime = MyTimeForm(prefix='mainTimeForm')
    if request.method == 'POST':
        if 'singleInputSubmit' in request.POST:
            # print("Single input work")
            for formInList in [sublist[6] for sublist in lastRunsData]:
                if f"{formInList.prefix}-start_time_input" in request.POST and f"{formInList.prefix}-end_time_input" in request.POST:
                    form = TimeForm(request.POST, prefix=formInList.prefix)
                    if form.is_valid():
                        startTime = form.cleaned_data['start_time_input']
                        endTime = form.cleaned_data['end_time_input']
                        errorInformation = try_save_runningLap(form.prefix, startTime, endTime)
                        if errorInformation is not None:
                            print(errorInformation)
                            messages.success(request, errorInformation)
                    else:
                        print("NOT VALID")
        elif 'checkBoxSubmit' in request.POST and 'mainTimeForm-time_input' in request.POST:
            # print("Checkbox work")
            selected_items = request.POST.getlist('selected_items')
            mainTimeData = request.POST.get('mainTimeForm-time_input')
            errorInformation = save_multiple_runningLaps(selected_items, mainTimeData)
            if errorInformation:
                print(errorInformation)
                for error in errorInformation:
                    messages.success(request, error)
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
