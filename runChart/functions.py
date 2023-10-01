from .models import *
from datetime import datetime, time, timedelta
import pytz
from django.db.models import Max, F
from django.utils import timezone

def get_runner_actual_laps_and_status():
    result = []
    lastRuns = get_last_run_for_every_runner(False)
    for lastRun in lastRuns:
        status = 'BIEGNIE' if lastRun.endLapDate is None else 'ODPOCZYWA'
        if status == 'BIEGNIE':
            startLapDateDatetime = datetime(lastRun.startLapDate.year, lastRun.startLapDate.month, lastRun.startLapDate.day, lastRun.startLapDate.hour, lastRun.startLapDate.minute)
            startLapDateDatetime += timedelta(hours=2)
            #timeDelta = datetime(2023, 10, 22, 9, 30) - startLapDateDatetime
            timeDelta = datetime.now() - startLapDateDatetime
            result.append([lastRun.runnerId.id, lastRun.runnerId.name, lastRun.runnerId.surname, lastRun.numberOfLaps-1, str(timeDelta), status])
        else:
            result.append([lastRun.runnerId.id, lastRun.runnerId.name, lastRun.runnerId.surname, lastRun.numberOfLaps, '_______________', status])
    return result

def get_runner_laps_and_records():
    result = []
    lastRuns = get_last_run_for_every_runner(True)
    lastRuns = sorted(lastRuns, key=lambda run: (-run.numberOfLaps, str(run.endLapDate)))
    for rank, lastRun in enumerate(lastRuns):
        shortestTime = get_best_time_for_runner(lastRun.runnerId)
        longestTime = get_longest_run_without_breaks_for_runner(lastRun.runnerId)
        if lastRun.endLapDate is None:
            result.append([lastRun.runnerId.id, lastRun.runnerId.name, lastRun.runnerId.surname, rank+1, lastRun.numberOfLaps - 1, shortestTime, longestTime])
        else:
            result.append([lastRun.runnerId.id, lastRun.runnerId.name, lastRun.runnerId.surname, rank+1, lastRun.numberOfLaps, shortestTime, longestTime])
    return result

def get_actual_ranking(lastRuns):
    ranking = []
    print(lastRuns)
    return ranking

def get_longest_run_without_breaks_for_runner(runnerId):
    runs = RunningLap.objects.filter(runnerId=runnerId).order_by('startLapDate')
    longest_time = timedelta(0)
    current_time = timedelta(0)
    previous_run_end = None
    for run in runs:
        if previous_run_end is None:
            previous_run_end = run.startLapDate
        if previous_run_end.hour == run.startLapDate.hour and previous_run_end.minute == run.startLapDate.minute and run.endLapDate is not None:
            # print(f"{previous_run_end} {run.startLapDate}")
            current_time += run.endLapDate - run.startLapDate
        elif previous_run_end != run.startLapDate and run.endLapDate is not None:
            # print(f"KURWA {previous_run_end} {run.startLapDate}")
            current_time = run.endLapDate - run.startLapDate
        else:
            break
        if current_time > longest_time:
            longest_time = current_time
        previous_run_end = run.endLapDate
    return longest_time

    # runs = RunningLap.objects.filter(runnerId=runnerId)
    #
    # longest_time = timedelta(0)
    # time = timedelta(0)
    # endLapTime = runs[0].startLapDate
    # for run in runs:
    #     if time > longest_time:
    #         longest_time = time
    #     if endLapTime == run.startLapDate and run.endLapDate is not None:
    #         time += run.endLapDate - run.startLapDate
    #         endLapTime = run.endLapDate
    # return longest_time

def get_best_time_for_runner(runnerId):
    runs = RunningLap.objects.filter(runnerId=runnerId)
    shortest_time = timedelta.max if runs else None
    for run in runs:
        time = run.endLapDate - run.startLapDate if run.endLapDate is not None else None
        if time is not None and time < shortest_time:
            shortest_time = time
    if shortest_time == timedelta.max:
        shortest_time = None
    return shortest_time

def get_last_run_for_every_runner(finished):
    lastRuns = []
    if finished:
        max_laps_per_runner = RunningLap.objects.exclude(endLapDate=None).values('runnerId').annotate(numberOfLaps=Max('numberOfLaps'))
    else:
        max_laps_per_runner = RunningLap.objects.values('runnerId').annotate(numberOfLaps=Max('numberOfLaps'))
    for m in max_laps_per_runner:
        lastRuns.append(RunningLap.objects.filter(runnerId=m['runnerId'], numberOfLaps=m['numberOfLaps']).first())
    return lastRuns

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
