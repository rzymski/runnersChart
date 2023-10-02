from django.shortcuts import render
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

# def adminAddRecord(request):
#     if request.method == "POST":
#     return render(request, 'admin/add.html')
# def adminEditRecord(request):
#     return render(request, 'admin/edit.html')
# def adminDeleteRecord(request):
#     return render(request, 'admin/add.html')

def customAdmin(request):
    print()
    lastRunsData = get_runner_actual_laps_and_status()
    return render(request, 'admin/customAdmin.html', {"lastRunsData": lastRunsData, "table_script": 'tableAdmin'})

def resultTable(request):
    runsData = get_runner_laps_and_records()
    return render(request, 'table/result.html', {"runsData": runsData, "table_script": 'tableUser'})


from django.forms.models import formset_factory


def xd(request):
    runners = [1, 2, 3, 4, 5]
    NameFormSet = formset_factory(nameForm, extra=len(runners))

    if request.method == 'POST':
        print("POST WYKONAL SIE")
        formset = NameFormSet(request.POST, prefix='name')
        if formset.is_valid():
            print("FORM IS VALID")
            for i, form in enumerate(formset):
                runner_id = runners[i]
                #name = form.cleaned_data['name_input']
                print(form)
        else:
            print("FORM IS NOT VALID")
    else:
        formset = NameFormSet(prefix='name')

    context = {
        'runner_ids': runners,
        'formset': formset,
    }
    return render(request, 'test/xd.html', context)

# def xd(request):
#     xd = [[0, 1], [1, 10], [2, 100], [3, 1000]]
#
#     TimeFormset = formset_factory(nameForm, extra=10)
#     if request.method == "POST":
#         formset = TimeFormset(request.POST, request.FILES)
#         if formset.is_valid():
#             print("FormSet is valid")
#         else:
#             print("FormSet is not valid")
#     else:
#         formset = TimeFormset()
#     return render(request, "test/xd.html", {"formset": formset})

    # if request.method == "POST":
    #     print("Przeslano cos")
        # form = timeForm(request.POST)
        # if form.is_valid():
        #     time = form.cleaned_data['time_input']
        #     print(time)
        # else:
        #     print("Form is not valid")
    #return render(request, 'test/xd.html', {"lastRunsData": xd, 'forms': forms})

# def xd(request):
#     if request.method == "POST":
#         form = runTimeForm(request.POST)
#         if form.is_valid():
#             name = form.cleaned_data['name_input']
#             date = form.cleaned_data['date_input']
#             time = form.cleaned_data['time_input']
#             print("Name:", name)
#             print("Date:", date)
#             print("Time:", time)
#         else:
#             print("Form is not valid")
#     form = runTimeForm()
#     return render(request, 'test/xd.html', {'form': form})


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
