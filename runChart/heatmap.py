"""Dane do mapy okrążeń.

Kolor oznacza NUMER okrążenia w przedziale od startLapDate do endLapDate.
Odstępy pomiędzy okrążeniami mają kolor 0 (brak aktywnego okrążenia).
Czas liczymy w UTC, żeby uniknąć błędów przy zmianie czasu w październiku.
"""

from collections import defaultdict
from datetime import timedelta, timezone as datetime_timezone

from django.conf import settings
from django.utils import timezone

from .models import Runner, RunningLap


# 0 = przerwa / brak aktywnego okrążenia, 1..9 = numer okrążenia,
# 10+ = wspólny kolor; w dymku widoczny dokładny numer okrążenia.
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
    (10, "#212121", "10+"),
)


def _local(dt):
    return timezone.localtime(dt, timezone.get_current_timezone())


def _new_segment(start, end, lap_number, timeline_start, timeline_seconds, kind):
    """Procentowe współrzędne pojedynczego odcinka na osi czasu."""
    left = 100 * (start - timeline_start).total_seconds() / timeline_seconds
    width = 100 * (end - start).total_seconds() / timeline_seconds
    return {
        'left': round(left, 6),
        'width': round(width, 6),
        'lap_number': lap_number,
        'band': min(lap_number, 10),
        'kind': kind,  # 'lap', 'break', 'open'
        'start_label': _local(start).strftime('%d.%m %H:%M %Z'),
        'end_label': _local(end).strftime('%d.%m %H:%M %Z'),
    }


def get_heatmap_context():
    """Dwa zapytania SQL niezależnie od liczby zawodników i okrążeń."""
    start = settings.FIRST_DAY
    if timezone.is_naive(start):
        start = timezone.make_aware(start, timezone.get_current_timezone())
    start = start.astimezone(datetime_timezone.utc)
    now = timezone.now().astimezone(datetime_timezone.utc)

    runners = list(Runner.objects.order_by('id').values('id', 'name', 'surname', 'finished'))
    laps = list(
        RunningLap.objects.order_by('startLapDate', 'numberOfLaps', 'pk').values(
            'runnerId_id', 'startLapDate', 'endLapDate', 'numberOfLaps'
        )
    )

    # 'Otwarte' okrążenie (endLapDate=NULL) rysujemy tylko, gdy bieg rzeczywiście
    # jest w trakcie. W archiwalnych danych nie znamy daty jego zakończenia.
    is_live = start <= now <= start + timedelta(hours=48)
    latest_activity = max(
        (dt.astimezone(datetime_timezone.utc)
         for lap in laps
         for dt in (lap['startLapDate'], lap['endLapDate']) if dt is not None),
        default=start,
    )
    if is_live:
        latest_activity = max(latest_activity, now)

    # Nie rozciągamy osi na wiele miesięcy wskutek błędnej daty FIRST_DAY.
    date_mismatch = bool(laps) and (
        latest_activity < start - timedelta(days=1)
        or latest_activity > start + timedelta(hours=48)
    )
    end = (start + timedelta(hours=12) if date_mismatch else
           max(start + timedelta(hours=12), latest_activity + timedelta(minutes=30)))
    span_seconds = (end - start).total_seconds()

    runs_by_runner = defaultdict(list)
    for lap in laps:
        lap_start = lap['startLapDate'].astimezone(datetime_timezone.utc)
        lap_finish = (lap['endLapDate'].astimezone(datetime_timezone.utc)
                      if lap['endLapDate'] is not None else None)
        if lap['numberOfLaps'] > 0 and (lap_finish is None or lap_finish > lap_start):
            runs_by_runner[lap['runnerId_id']].append(
                (lap_start, lap_finish, lap['numberOfLaps'])
            )

    rows = []
    for runner in runners:
        segments = []
        cursor = start
        completed_laps = 0
        for lap_start, lap_finish, lap_number in runs_by_runner[runner['id']]:
            # Tylko ZAKOŃCZONE okrążenia wpływają na kolumnę „Okr.”.
            if lap_finish is not None and start <= lap_finish <= end:
                completed_laps = max(completed_laps, lap_number)

            if lap_finish is None:
                if not is_live:
                    continue
                observed_end = now
                kind = 'open'
            else:
                observed_end = lap_finish
                kind = 'lap'

            # Ucinamy odcinek do zakresu wykresu. W razie niepoprawnych,
            # nachodzących na siebie danych nie rysujemy odcinków wstecz.
            visible_start = max(start, lap_start, cursor)
            visible_end = min(end, observed_end)
            if visible_end <= visible_start:
                continue
            if visible_start > cursor:
                segments.append(_new_segment(cursor, visible_start, 0, start, span_seconds, 'break'))
            segments.append(_new_segment(
                visible_start, visible_end, lap_number, start, span_seconds, kind
            ))
            cursor = visible_end

        if cursor < end:
            segments.append(_new_segment(cursor, end, 0, start, span_seconds, 'break'))

        rows.append({
            'id': runner['id'],
            'name': f"{runner['name']} {runner['surname']}",
            'sort_name': f"{runner['surname']} {runner['name']}",
            'laps': completed_laps,
            'finished': runner['finished'],
            'segments': segments,
        })

    rows.sort(key=lambda row: (-row['laps'], row['id']))

    ticks = [{'label': _local(start).strftime('%H:%M'), 'left': 0, 'edge': 'start'}]
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
    # Podczas zmiany czasu 02:00 w Polsce występuje dwukrotnie.
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
