from .models import *
from datetime import datetime, time, timedelta
from django.db.models import Max, F, Q
from django.utils import timezone
from django.conf import settings
from .race_time import race_datetime, utc_elapsed, local_clock_label, is_ambiguous

FIRST_DAY = settings.FIRST_DAY
SECOND_DAY = settings.SECOND_DAY


def save_multiple_runningLaps(runnerIds, time_str, second_hour=False):
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
            error = try_save_runningLap(int(runnerId), None, timeValue, end_second_hour=second_hour)
        else:
            error = try_save_runningLap(int(runnerId), timeValue, None, start_second_hour=second_hour)
        if error:
            errorInformation.append(error)
    return errorInformation


def try_save_runningLap(runnerId, startTime=None, endTime=None, start_second_hour=False, end_second_hour=False):
    errorTime = startTime if startTime is not None else endTime
    if startTime and time(21, 00) > startTime > time(12, 30) or endTime and time(21, 00) > endTime > time(12, 30):
        return f"Podano zly czas {errorTime}. Wyscig nie trwa pomiedzy 12:30 i 21:00, bo to nocny bieg."
    runner = Runner.objects.get(pk=runnerId)
    errorInformation = None
    if startTime:
        errorInformation = save_running_lap(
            runner, startTime, start_second_hour=start_second_hour
        )
    elif endTime:
        lap = RunningLap.objects.filter(runnerId=runnerId).order_by('-startLapDate').first()
        if lap is None:
            return f'Zawodnik {runner} nie ma rozpoczętego okrążenia.'
        if lap.endLapDate is not None:
            return f'Zawodnik {runner} nie ma otwartego okrążenia.'
        try:
            endLapDate = race_datetime(endTime, end_second_hour)
        except ValueError as exc:
            return str(exc)
        if endLapDate >= lap.startLapDate:
            lap.endLapDate = endLapDate
            lap.save(update_fields=['endLapDate'])
        else:
            errorInformation = (f"Podano zly czas {errorTime}. Zawodnik {runner} "
                                "nie moze zakonczyc okrazenia przed jego rozpoczeciem")
    else:
        errorInformation = "Nie otrzymano ani czasu rozpoczecia ani zakonczenia"
    return errorInformation


def save_running_lap(runner, start_lap_time, end_lap_time=None,
                     start_second_hour=False, end_second_hour=False):
    try:
        startLapDate = race_datetime(start_lap_time, start_second_hour)
        endLapDate = race_datetime(end_lap_time, end_second_hour)
    except ValueError as exc:
        return str(exc)
    if endLapDate is not None and endLapDate < startLapDate:
        return f"Podano zly czas {end_lap_time}. Koniec okrazenia poprzedza poczatek."
    if RunningLap.objects.filter(runnerId=runner, endLapDate__gt=startLapDate).exists():
        return (f"Podano zly czas {start_lap_time}. Zawodnik {runner} "
                "nie moze zaczynac okrazenia przed zakonczeniem poprzedniego")
    if RunningLap.objects.filter(runnerId=runner, endLapDate__isnull=True).exists():
        return f"Zawodnik {runner} ma juz otwarte okrazenie."
    numberOfLaps = RunningLap.objects.filter(
        runnerId=runner, startLapDate__lt=startLapDate
    ).count() + 1
    RunningLap.objects.create(runnerId=runner, startLapDate=startLapDate,
                              endLapDate=endLapDate, numberOfLaps=numberOfLaps)
    return None


def get_runner_actual_laps_and_status():
    result = []
    lastRuns = get_last_run_for_every_runner(False)
    for lastRun in lastRuns:
        status = 'ZAKOŃCZYŁ' if lastRun.runnerId.finished else ('BIEGNIE' if lastRun.endLapDate is None else 'ODPOCZYWA')
        if status == 'BIEGNIE':
            startLapDateDatetime = lastRun.startLapDate
            timeDelta = utc_elapsed(startLapDateDatetime, timezone.now())
            hours, remainder = divmod(timeDelta.total_seconds(), 3600)
            minutes, _ = divmod(remainder, 60)
            timeDeltaStr = f"{int(hours)}h i {int(minutes)} minut temu" if timezone.now() > startLapDateDatetime else "nie rozpoczeto jeszcze"
            result.append([lastRun.runnerId.id, lastRun.runnerId.name, lastRun.runnerId.surname, lastRun.numberOfLaps-1, timeDeltaStr, status])
        elif status == 'ODPOCZYWA':
            result.append([lastRun.runnerId.id, lastRun.runnerId.name, lastRun.runnerId.surname, lastRun.numberOfLaps, '_______________', status])
        else:
            if lastRun.endLapDate:
                result.append([lastRun.runnerId.id, lastRun.runnerId.name, lastRun.runnerId.surname, lastRun.numberOfLaps, '_______________', status])
            else:
                result.append([lastRun.runnerId.id, lastRun.runnerId.name, lastRun.runnerId.surname, lastRun.numberOfLaps-1, '_______________', status])
    return result


def get_runner_laps_and_records():
    result = []
    lastRuns = get_last_run_for_every_runner(True)
    lastRuns = sorted(lastRuns, key=lambda run: (-run.numberOfLaps, run.endLapDate))

    allRunners = Runner.objects.all()
    runnersWithLaps = {run.runnerId.id for run in lastRuns}

    for rank, lastRun in enumerate(lastRuns):
        shortestTime = get_best_time_for_runner(lastRun.runnerId)
        longestTime = get_longest_run_without_breaks_for_runner(lastRun.runnerId)
        end = timezone.localtime(lastRun.endLapDate)
        endTime = end.strftime("%Y-%m-%d  %H:%M")
        if is_ambiguous(end):
            endTime += ' (II)' if end.fold else ' (I)'
        runsOfThisRunner = RunningLap.objects.filter(runnerId=lastRun.runnerId)
        status = 'ZAKOŃCZYŁ' if lastRun.runnerId.finished else ('BIEGNIE' if len(runsOfThisRunner) != lastRun.numberOfLaps else 'ODPOCZYWA')
        result.append([lastRun.runnerId.id, lastRun.runnerId.name, lastRun.runnerId.surname, rank+1, lastRun.numberOfLaps, shortestTime, longestTime, endTime, status])

    for runner in allRunners:
        if runner.id not in runnersWithLaps:
            result.append([runner.id, runner.name, runner.surname, '___', 0, '_______', '_______', '___________________', ""])

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
        if previous_run_end == run.startLapDate and run.endLapDate is not None:
            current_time += utc_elapsed(run.startLapDate, run.endLapDate)
        elif previous_run_end != run.startLapDate and run.endLapDate is not None:
            current_time = utc_elapsed(run.startLapDate, run.endLapDate)
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
        run_time = utc_elapsed(run.startLapDate, run.endLapDate) if run.endLapDate is not None else None
        if run_time is not None and run_time < shortest_time:
            shortest_time = run_time
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

    allRunners = list(Runner.objects.all())

    for run in runningLaps:
        if run.runnerId is not None:
            runner = Runner.objects.get(pk=run.runnerId.id)
            index = allRunners.index(runner)
            result[index].append({'x': local_clock_label(run.startLapDate), 'y': run.numberOfLaps - 1})
            if run.endLapDate is not None:
                result[index].append({'x': local_clock_label(run.endLapDate), 'y': run.numberOfLaps})
    return result


def get_laps_for_every_time():
    runningLapStartDates = list(RunningLap.objects.values_list('startLapDate', flat=True).distinct().order_by('startLapDate'))
    runningLapEndDatesWithNones = list(RunningLap.objects.values_list('endLapDate', flat=True).distinct().order_by('endLapDate'))
    runningLapEndDates = list(filter(lambda x: x is not None, runningLapEndDatesWithNones))
    runningLapsDates = sorted(runningLapStartDates + runningLapEndDates)
    # Keep UTC instants as keys: local wall times with fold=0/1 can compare equal.
    run_dict = {dt: [0] * Runner.objects.count() for dt in runningLapsDates}
    runners = Runner.objects.all()
    for startLapDate in run_dict:
        for index, runner in enumerate(runners):
            run_dict[startLapDate][index] = get_max_laps_for_runner_before_date(runner.id, startLapDate)
    return run_dict


def get_max_laps_for_runner_before_date(runner_id, start_lap_date):
    max_laps = RunningLap.objects.filter(
        runnerId=runner_id,
        startLapDate__lte=start_lap_date
    ).order_by('-numberOfLaps').first()
    if max_laps:
        return max_laps.numberOfLaps
    else:
        return 0
