from django.shortcuts import render
from .models import *
from .functions import *
from datetime import datetime, time
import pytz

from .forms import runTimeForm

def resultTable(request):
    get_runner_actual_laps_and_status()
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
    return render(request, 'test/xd.html', {'form': form})

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
