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
    if request.method == 'POST':
        for formInList in [sublist[6] for sublist in lastRunsData]:
            if f"{formInList.prefix}-start_time_input" in request.POST and f"{formInList.prefix}-end_time_input" in request.POST:
                form = timeForm(request.POST, prefix=formInList.prefix)
                if form.is_valid():
                    startTime = form.cleaned_data['start_time_input']
                    endTime = form.cleaned_data['end_time_input']
                    print(f"Form Data for prefix={form.prefix} startTime={startTime} endTime={endTime}")
                    errorInformation = try_save_runningLap(form.prefix, startTime, endTime)
                    print(errorInformation)
                else:
                    print("NOT VALID")
        return redirect('customAdmin')
    return render(request, 'admin/customAdmin.html', {"lastRunsData": lastRunsData, "table_script": 'tableAdmin'})

def resultTable(request):
    runsData = get_runner_laps_and_records()
    return render(request, 'table/result.html', {"runsData": runsData, "table_script": 'tableUser'})

def form(request):
    lastRunsData = get_runner_actual_laps_and_status()
    for index, lastRun in enumerate(lastRunsData, 1):
        lastRun.append(timeForm(prefix=str(index)))
    mainTime = MyTimeForm(prefix='mainTimeForm')
    if request.method == 'POST':
        print(request.POST)
        if 'singleInputSubmit' in request.POST:
            print("Single input work")
            for formInList in [sublist[6] for sublist in lastRunsData]:
                if f"{formInList.prefix}-start_time_input" in request.POST and f"{formInList.prefix}-end_time_input" in request.POST:
                    form = timeForm(request.POST, prefix=formInList.prefix)
                    if form.is_valid():
                        startTime = form.cleaned_data['start_time_input']
                        endTime = form.cleaned_data['end_time_input']
                        print(f"Form Data for prefix={form.prefix} startTime={startTime} endTime={endTime}")
                        errorInformation = try_save_runningLap(form.prefix, startTime, endTime)
                        print(errorInformation) if errorInformation is not None else print("BRAK BLEDOW")
                    else:
                        print("NOT VALID")
        elif 'checkBoxSubmit' in request.POST and 'mainTimeForm-time_input' in request.POST:
            print("Checkbox work")
            selected_items = request.POST.getlist('selected_items')
            mainTimeData = request.POST.get('mainTimeForm-time_input')
            errorInformation = save_multiple_runningLaps(selected_items, mainTimeData)
            print(errorInformation) if errorInformation is not None else print("BRAK BLEDOW")
        return redirect('myForm')
    return render(request, 'test/form.html', {"lastRunsData": lastRunsData, "table_script": 'tableAdmin', 'mainTime': mainTime})
    # items = [1,2,3,4,5,6,7,8,9,10]
    # if request.method == 'POST':
    #     selected_items = request.POST.getlist('selected_items')
    #     print("Zaznaczone elementy:", selected_items)
    # return render(request, 'test/form.html', {'items': items})

def xd(request):
    form_list = [timeForm(prefix=str(i)) for i in range(5)]

    print(form_list)

    if request.method == 'POST':
        for form in form_list:
            if f"{form.prefix}-time_input" in request.POST:
                form = MyTimeForm(request.POST, prefix=form.prefix)
                if form.is_valid():
                    time = form.cleaned_data['time_input']
                    print(f"Form Data for prefix={form.prefix} time={time}")
                else:
                    print("NOT VALID")
        return redirect('xd')
    return render(request, 'test/xd.html', {'form_list': form_list})



# def form(request):
#     runners = [1, 2, 3, 4, 5]
#
#     MyFormSet = formset_factory(MyForm, extra=5)
#     formset = MyFormSet()
#
#     context = {
#         'runner_ids': runners,
#         'formset': formset,
#     }
#
#     return render(request, 'test/form.html', context)

# def form(request):
#     exampleList = [1, 2, 3, 4, 5]
#     form = MyForm()
#
#     if request.method == 'POST':
#         form = MyForm(request.POST)
#         if form.is_valid():
#             char_value = form.cleaned_data['char_field']
#             time_value = form.cleaned_data['time_field']
#             # Process the form data as needed
#             print(f"{char_value} {time_value}")
#         else:
#             print(f"Nie dobrze ale cos przeslalo {form}")
#
#     context = {
#         'exampleList': exampleList,
#         'form': form,
#     }
#
#     return render(request, 'test/form.html', context)

# def form(request):
#     exampleList = [1, 2, 3, 4, 5]
#
#     if request.method == 'POST':
#         form = ExampleListForm(exampleList, request.POST)
#         if form.is_valid():
#             # Process the checked checkboxes
#             checked_items = [item for item in exampleList if form.cleaned_data.get(f'checkbox_{item}')]
#             print("Checked items:", checked_items)
#             # Do something with the checked items
#
#     else:
#         form = ExampleListForm(exampleList)
#
#     return render(request, 'test/form.html', {'form': form})

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
