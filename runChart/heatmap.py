from collections import defaultdict
from datetime import timedelta, timezone as datetime_timezone

from django.conf import settings
from django.utils import timezone

from .models import Runner, RunningLap


LAP_COLORS = (
    (0, "#e9ecef", "0"),
    (1, "#ef4444", "1"),
    (2, "#f97316", "2"),
    (3, "#facc15", "3"),
    (4, "#84cc16", "4"),
    (5, "#0ea5e9", "5"),
    (6, "#6366f1", "6"),
    (7, "#a855f7", "7"),
    (8, "#ab47bc", "8"),
    (9, "#311b92", "9"),
    (10, "#212121", "10+")
)


def _local(dt):
    return timezone.localtime(dt, timezone.get_current_timezone())


def _color_band(lap_count):
    return min(lap_count, 10)


def _new_segment(start, end, laps, timeline_start, timeline_seconds):
    """Współrzędne w procentach zapewniają płynną skalę czasu."""
    left = 100 * (start - timeline_start).total_seconds() / timeline_seconds
    width = 100 * (end - start).total_seconds() / timeline_seconds
    return {
        'left': round(left, 6),
        'width': round(width, 6),
        'laps': laps,
        'band': _color_band(laps),
        'start_label': _local(start).strftime('%d.%m %H:%M %Z'),
        'end_label': _local(end).strftime('%d.%m %H:%M %Z'),
    }


def get_heatmap_context():
    """Dwa zapytania niezależnie od liczby biegaczy i okrążeń."""
    start = settings.FIRST_DAY
    if timezone.is_naive(start):
        start = timezone.make_aware(start, timezone.get_current_timezone())
    # UTC do rachunków: podczas październikowej zmiany czasu godzina 02:00
    # w Polsce występuje dwukrotnie, a oś nadal musi być monotoniczna.
    start = start.astimezone(datetime_timezone.utc)

    runners = list(Runner.objects.order_by('id').values('id', 'name', 'surname', 'finished'))
    laps = list(
        RunningLap.objects.order_by('endLapDate', 'numberOfLaps', 'pk').values(
            'runnerId_id', 'startLapDate', 'endLapDate', 'numberOfLaps'
        )
    )

    # Zawsze pokaż przynajmniej 12 godzin. Jeśli bieg trwa dłużej,
    # rozciągnij oś do 30 min po ostatniej zarejestrowanej aktywności.
    latest_activity = max(
        (dt.astimezone(datetime_timezone.utc) for lap in laps for dt in (lap['startLapDate'], lap['endLapDate']) if dt is not None),
        default=start,
    )
    # Chroni stronę przed tysiącami znaczników osi, gdy FIRST_DAY
    # przez pomyłkę wskazuje poprzednią edycję wydarzenia.
    date_mismatch = bool(laps) and (
        latest_activity < start - timedelta(days=1)
        or latest_activity > start + timedelta(hours=48)
    )
    end = (start + timedelta(hours=12) if date_mismatch else
           max(start + timedelta(hours=12), latest_activity + timedelta(minutes=30)))
    span_seconds = (end - start).total_seconds()

    completions = defaultdict(list)
    for lap in laps:
        finish = lap['endLapDate'].astimezone(datetime_timezone.utc) if lap['endLapDate'] else None
        # Otwarte okrążenie NIE zwiększa wyniku.
        if finish is not None and finish >= start and lap['numberOfLaps'] > 0:
            completions[lap['runnerId_id']].append((finish, lap['numberOfLaps']))

    rows = []
    for runner in runners:
        segments = []
        last_time = start
        count = 0
        # Dzięki sortowaniu na poziomie SQL wyniki biegaczy są chronologiczne.
        for finish, lap_number in completions[runner['id']]:
            if finish > end:
                break
            if finish > last_time:
                segments.append(_new_segment(last_time, finish, count, start, span_seconds))
                last_time = finish
            count = max(count, lap_number)
        if last_time < end:
            segments.append(_new_segment(last_time, end, count, start, span_seconds))

        rows.append({
            'id': runner['id'],
            'name': f"{runner['name']} {runner['surname']}",
            'sort_name': f"{runner['surname']} {runner['name']}",
            'laps': count,
            'finished': runner['finished'],
            'segments': segments,
        })

    # Najwięcej ukończonych okrążeń na górze, przy remisie numer startowy.
    rows.sort(key=lambda row: (-row['laps'], row['id']))

    ticks = [{'label': _local(start).strftime('%H:%M'), 'left': 0, 'edge': 'start'}]
    # Kolejne pełne godziny, także po północy (z oznaczeniem nowej daty).
    cursor = start.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    while cursor < end:
        local_cursor = _local(cursor)
        ticks.append({
            'label': local_cursor.strftime('%H:%M'),
            'left': round(100 * (cursor - start).total_seconds() / span_seconds, 6),
            'edge': 'middle',
            'tz_name': local_cursor.strftime('%Z'),
            'new_day': local_cursor.strftime('%d.%m') if local_cursor.hour == 0 else '',
        })
        cursor += timedelta(hours=1)
    ticks.append({'label': _local(end).strftime('%H:%M'), 'left': 100, 'edge': 'end'})
    # Odróżnij dwa wystąpienia tej samej godziny podczas zmiany CEST -> CET.
    for index in range(1, len(ticks) - 2):
        first, second = ticks[index], ticks[index + 1]
        if first['label'] == second['label'] and first['edge'] == second['edge'] == 'middle':
            first['tz_label'] = first['tz_name']
            second['tz_label'] = second['tz_name']

    return {
        'heatmap_rows': rows,
        'heatmap_ticks': ticks,
        'heatmap_colors': LAP_COLORS,
        'heatmap_start': _local(start),
        'heatmap_end': _local(end),
        'heatmap_runner_count': len(rows),
        'heatmap_laps_count': sum(row['laps'] for row in rows),
        'heatmap_axis_min_width': max(1120, round(span_seconds / 3600 * 85)),
        'heatmap_config_warning': date_mismatch,
    }
