from .models import *
from datetime import datetime, time, timedelta
import pytz
from django.db.models import Max, F, Q
from django.utils import timezone

def save_multiple_runningLaps(runnerIds, time_str):
    if time_str is None or time_str == '':
        return "Nie podano czasu"
    try:
        timeValue = datetime.strptime(time_str, '%H:%M:%S').time()
    except ValueError:
        try:
            timeValue = datetime.strptime(time_str, '%H:%M').time()
        except ValueError:
            return "Nie właściwy format czasu"
    errorInformation = []

    for runnerId in runnerIds:
        lap = RunningLap.objects.filter(runnerId=int(runnerId)).latest('startLapDate')
        if lap.endLapDate is None:
            error = try_save_runningLap(int(runnerId), None, timeValue)
        else:
            error = try_save_runningLap(int(runnerId), timeValue, None)
        if error:
            errorInformation.append(error)
    return errorInformation

def try_save_runningLap(runnerId, startTime=None, endTime=None):
    errorTime = startTime if startTime is not None else endTime
    if startTime and time(21, 00) > startTime > time(12, 30) or endTime and time(21, 00) > endTime > time(12, 30):
        return f"Podano zly czas {errorTime}. Wyscig nie trwa pomiedzy 12:30 i 21:00, bo to nocny bieg."
    runner = Runner.objects.get(pk=runnerId)
    errorInformation = None
    if startTime:
        errorInformation = save_running_lap(runner, startTime)
    elif endTime:
        lap = RunningLap.objects.filter(runnerId=runnerId).latest('startLapDate')
        if endTime >= time(21, 30):
            endLapDate = timezone.make_aware(
                datetime(2023, 10, 21, endTime.hour, endTime.minute))
        else:
            endLapDate = timezone.make_aware(
                datetime(2023, 10, 22, endTime.hour, endTime.minute))
        if endLapDate >= lap.startLapDate:
            lap.endLapDate = endLapDate
            lap.save()
        else:
            errorInformation = f"Podano zly czas {errorTime}. Zawodnik {runner} nie moze zakonczyc okrazenia przed jego rozpoczeciem"
    else:
        errorInformation = "Nie otrzymano ani czasu rozpoczecia ani zakonczenia"
    return errorInformation if errorInformation is not None else None

def save_running_lap(runner, start_lap_time, end_lap_time=None):
    startLapDate = None
    endLapDate = None
    if start_lap_time >= time(21, 30):
        startLapDate = timezone.make_aware(
            datetime(2023, 10, 21, start_lap_time.hour, start_lap_time.minute))
    else:
        startLapDate = timezone.make_aware(
            datetime(2023, 10, 22, start_lap_time.hour, start_lap_time.minute))
    if end_lap_time is not None:
        if end_lap_time >= time(21, 30):
            endLapDate = timezone.make_aware(
                datetime(2023, 10, 21, end_lap_time.hour, end_lap_time.minute))
        else:
            endLapDate = timezone.make_aware(
                datetime(2023, 10, 22, end_lap_time.hour, end_lap_time.minute))
    errorQuery = Q(runnerId=runner, endLapDate__gt=startLapDate)
    numberOfErrorLaps = RunningLap.objects.filter(errorQuery).count()
    if numberOfErrorLaps > 0:
        return f"Podano zly czas {start_lap_time}. Zawodnik {runner} nie moze zaczynac okrazenia przed zakonczeniem poprzedniego"
    query = Q(runnerId=runner, startLapDate__lt=startLapDate)
    numberOfLaps = RunningLap.objects.filter(query).count() + 1
    new_running_lap = RunningLap(runnerId=runner, startLapDate=startLapDate, endLapDate=endLapDate, numberOfLaps=numberOfLaps)
    new_running_lap.save()
    return None

def get_runner_actual_laps_and_status():
    result = []
    lastRuns = get_last_run_for_every_runner(False)
    for lastRun in lastRuns:
        status = 'BIEGNIE' if lastRun.endLapDate is None else 'ODPOCZYWA'
        if status == 'BIEGNIE':
            startLapDateDatetime = datetime(lastRun.startLapDate.year, lastRun.startLapDate.month, lastRun.startLapDate.day, lastRun.startLapDate.hour, lastRun.startLapDate.minute)
            startLapDateDatetime += timedelta(hours=2)
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

def get_actual_ranking(run):
    runs_before = RunningLap.objects.filter(endLapDate__lt=run.endLapDate, numberOfLaps=run.numberOfLaps)
    distinct_runner_count = runs_before.values('runnerId').distinct().count()
    return distinct_runner_count+1

def get_longest_run_without_breaks_for_runner(runnerId):
    runs = RunningLap.objects.filter(runnerId=runnerId).order_by('startLapDate')
    longest_time = timedelta(0)
    current_time = timedelta(0)
    previous_run_end = None
    for run in runs:
        if previous_run_end is None:
            previous_run_end = run.startLapDate
        if previous_run_end.hour == run.startLapDate.hour and previous_run_end.minute == run.startLapDate.minute and run.endLapDate is not None:
            current_time += run.endLapDate - run.startLapDate
        elif previous_run_end != run.startLapDate and run.endLapDate is not None:
            current_time = run.endLapDate - run.startLapDate
        else:
            break
        if current_time > longest_time:
            longest_time = current_time
        previous_run_end = run.endLapDate
    return longest_time

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

    allRunners = list(Runner.objects.all())

    for run in runningLaps:
        if run.runnerId is not None:
            start_lap_date_warsaw = run.startLapDate.astimezone(warsaw_tz)
            runner = Runner.objects.get(pk=run.runnerId.id)
            index = allRunners.index(runner)
            result[index].append({'x': time(start_lap_date_warsaw.hour, start_lap_date_warsaw.minute).strftime('%H:%M'), 'y': run.numberOfLaps - 1})
            if run.endLapDate is not None:
                end_lap_date_warsaw = run.endLapDate.astimezone(warsaw_tz)
                result[index].append({'x': time(end_lap_date_warsaw.hour, end_lap_date_warsaw.minute).strftime('%H:%M'), 'y': run.numberOfLaps})
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
        for index, runner in enumerate(runners):
            dict[startLapDate][index] = get_max_laps_for_runner_before_date(runner.id, startLapDate)
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
