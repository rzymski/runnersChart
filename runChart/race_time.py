"""Clock-time entry for an overnight race spanning the autumn DST transition.

Database datetimes represent instants (UTC); the optional ``second_hour`` flag
selects the SECOND occurrence of the repeated 02:00-02:59 hour.  For all other
clock times the flag is immaterial.  No schema change is necessary.
"""
from datetime import datetime, timezone as utc_timezone
from zoneinfo import ZoneInfo

from django.conf import settings
from django.utils import timezone

UTC = utc_timezone.utc


def race_timezone():
    return ZoneInfo(settings.TIME_ZONE)


def is_ambiguous(local_datetime):
    """Whether this specific local wall time occurs twice on its calendar day."""
    zone = race_timezone()
    naive = local_datetime.replace(tzinfo=None)
    first = naive.replace(tzinfo=zone, fold=0)
    second = naive.replace(tzinfo=zone, fold=1)
    if first.utcoffset() == second.utcoffset():
        return False
    return all(
        candidate.astimezone(UTC).astimezone(zone).replace(tzinfo=None) == naive
        for candidate in (first, second)
    )


def race_datetime(clock_time, second_hour=False):
    """Convert an HH:MM (or TimeField value) to a UTC-aware race datetime.

    The race crosses midnight; a time at/after the start clock is on day one,
    and an earlier clock is on day two, mirroring existing form behavior.
    """
    if clock_time is None:
        return None
    race_start = settings.FIRST_DAY
    race_day = (settings.FIRST_DAY.date() if clock_time >= race_start.time()
                else settings.SECOND_DAY.date())
    local_wall = datetime.combine(race_day, clock_time).replace(tzinfo=None)
    zone = race_timezone()
    is_repeated = is_ambiguous(local_wall)
    candidate = local_wall.replace(tzinfo=zone, fold=int(bool(second_hour) and is_repeated))
    # Spring DST jump: some local wall times do not exist.
    if candidate.astimezone(UTC).astimezone(zone).replace(tzinfo=None) != local_wall:
        raise ValueError('Podana godzina nie istnieje w dniu zmiany czasu.')
    return candidate.astimezone(UTC)


def utc_elapsed(start, end):
    """Real elapsed time, not subtraction of two local ZoneInfo wall times."""
    return end.astimezone(UTC) - start.astimezone(UTC)


def local_clock_label(dt, with_day=False):
    """Avoid CET/CEST but distinguish the two occurrences of 02:xx."""
    local = timezone.localtime(dt, race_timezone())
    label = local.strftime('%d.%m %H:%M' if with_day else '%H:%M')
    if is_ambiguous(local):
        label += ' (II)' if local.fold else ' (I)'
    return label


def renumber_runner_laps(runner_id):
    """Keep lap numbers consecutive after Django Admin edits/imports/deletions."""
    from .models import RunningLap
    laps = RunningLap.objects.filter(runnerId_id=runner_id).order_by('startLapDate', 'pk')
    for number, lap in enumerate(laps, 1):
        if lap.numberOfLaps != number:
            RunningLap.objects.filter(pk=lap.pk).update(numberOfLaps=number)
