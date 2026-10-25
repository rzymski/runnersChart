from collections import defaultdict
from datetime import datetime, time, timedelta, timezone as datetime_timezone

from django.conf import settings
from django.utils import timezone

from .models import Runner, RunningLap
from .race_time import local_clock_label, race_timezone


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
        'start_label': local_clock_label(start, with_day=True),
        'end_label': local_clock_label(end, with_day=True),
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

    race_tz = race_timezone()
    start_local = start.astimezone(race_tz)
    end_local = datetime.combine(start_local.date() + timedelta(days=1), time(10, 0), tzinfo=race_tz)
    end = end_local.astimezone(datetime_timezone.utc)
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
        last_completed_at = None
        for lap_start, lap_finish, lap_number in runs_by_runner[runner['id']]:
            if lap_finish is not None and start <= lap_finish <= end:
                if (lap_number > completed_laps or
                        (lap_number == completed_laps and
                         (last_completed_at is None or lap_finish < last_completed_at))):
                    completed_laps = lap_number
                    last_completed_at = lap_finish

            if lap_finish is None:
                observed_end = min(now, end)
                kind = 'open'
            else:
                observed_end = lap_finish
                kind = 'lap'

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
            'last_finish_ts': int(last_completed_at.timestamp()) if last_completed_at else None,
            'finished': runner['finished'],
            'segments': segments,
        })

    rows.sort(key=lambda row: (
        -row['laps'],
        row['last_finish_ts'] if row['last_finish_ts'] is not None else float('inf'),
        row['id'],
    ))

    ticks = [{'label': local_clock_label(start), 'left': 0, 'edge': 'start'}]
    cursor = start.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    while cursor < end:
        local_cursor = _local(cursor)
        ticks.append({
            'label': local_clock_label(cursor),
            'left': round(100 * (cursor - start).total_seconds() / span_seconds, 6),
            'edge': 'middle',
            'new_day': local_cursor.strftime('%d.%m') if local_cursor.hour == 0 else '',
        })
        cursor += timedelta(hours=1)
    ticks.append({'label': local_clock_label(end), 'left': 100, 'edge': 'end'})

    return {
        'heatmap_rows': rows,
        'heatmap_ticks': ticks,
        'heatmap_colors': LAP_COLORS,
        'heatmap_start': _local(start),
        'heatmap_end': _local(end),
        'heatmap_runner_count': len(rows),
        'heatmap_laps_count': sum(row['laps'] for row in rows),
        'heatmap_axis_min_width': max(1120, round(span_seconds / 3600 * 85))
    }
