from .models import *
from datetime import datetime, time
import pytz
from django.db.models import Max, F


def get_runner_actual_laps_and_status():
    result = []
    max_laps_per_runner = RunningLap.objects.values('runnerId').annotate(numberOfLaps=Max('numberOfLaps'))
    for m in max_laps_per_runner:
        result.append(RunningLap.objects.filter(runnerId=m['runnerId'], numberOfLaps=m['numberOfLaps']).first())
    return result

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
    runningLaps = RunningLap.objects.all().order_by('startLapDate')
    warsaw_tz = pytz.timezone('Europe/Warsaw')

    runners = get_best_runners()

    for run in runningLaps:
        if run.runnerId is not None:
            start_lap_date_warsaw = run.startLapDate.astimezone(warsaw_tz)
            result[run.runnerId.id-1].append({'x': time(start_lap_date_warsaw.hour, start_lap_date_warsaw.minute).strftime('%H:%M'), 'y': run.numberOfLaps - 1})
            if run.endLapDate is not None:
                end_lap_date_warsaw = run.endLapDate.astimezone(warsaw_tz)
                result[run.runnerId.id-1].append({'x': time(end_lap_date_warsaw.hour, end_lap_date_warsaw.minute).strftime('%H:%M'), 'y': run.numberOfLaps})
            # Wersja z posortowanymi biegaczami wzgledem wyników (brak sprawdzenia null w endDate)
            # runnerIndex = runners.index(run.runnerId.__str__())
            # start_lap_date_warsaw = run.startLapDate.astimezone(warsaw_tz)
            # result[runnerIndex].append({'x': time(start_lap_date_warsaw.hour, start_lap_date_warsaw.minute).strftime('%H:%M'), 'y': run.numberOfLaps-1})
            # end_lap_date_warsaw = run.endLapDate.astimezone(warsaw_tz)
            # result[runnerIndex].append({'x': time(end_lap_date_warsaw.hour, end_lap_date_warsaw.minute).strftime('%H:%M'), 'y': run.numberOfLaps})
    return result

def get_laps_for_every_time():
    runningLapStartDates = list(RunningLap.objects.values_list('startLapDate', flat=True).distinct().order_by('startLapDate'))
    runningLapEndDatesWithNones = list(RunningLap.objects.values_list('endLapDate', flat=True).distinct().order_by('endLapDate'))
    runningLapEndDates = list(filter(lambda x: x is not None, runningLapEndDatesWithNones))
    runningLapsDates = sorted(runningLapStartDates + runningLapEndDates)

    print(len(runningLapsDates))

    europe_warsaw = pytz.timezone('Europe/Warsaw')
    running_laps = [dt.astimezone(europe_warsaw) for dt in runningLapsDates]
    dict = {running_lap: [0] * Runner.objects.count() for running_lap in running_laps}
    runners = Runner.objects.all()
    for startLapDate in dict:
        for runner in runners:
            dict[startLapDate][runner.id - 1] = get_max_laps_for_runner_before_date(runner.id, startLapDate)
    return dict

def get_max_laps_for_runner_before_date(runner_id, start_lap_date):
    max_laps = RunningLap.objects.filter(
        runnerId=runner_id,
        startLapDate__lte=start_lap_date
    ).order_by('-numberOfLaps').first()
    if max_laps:
        return max_laps.numberOfLaps
    else:
        return 0
