import csv
from datetime import datetime
from io import StringIO

from django import forms
from django.apps import apps
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin import widgets
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import path, reverse
from django.utils import timezone

from .models import Runner, RunningLap
from .race_time import (
    local_clock_label, race_datetime, renumber_runner_laps, utc_elapsed,
)


class CsvImportForm(forms.Form):
    csv_upload = forms.FileField()


def _import_clock(value):
    for fmt in ('%H:%M:%S', '%H:%M'):
        try:
            return datetime.strptime(value, fmt).time()
        except ValueError:
            pass
    raise ValueError(f'Nieprawidłowy format godziny: {value!r}')


def _import_second_hour(row, *names):
    for name in names:
        value = (row.get(name) or '').strip().lower()
        if value:
            if value not in ('0', '1', 'true', 'false'):
                raise ValueError(f'Pole {name} musi mieć wartość 0 lub 1.')
            return value in ('1', 'true')
    return False


def upload_csvFileUniversal(request, model_name):
    model = apps.get_model(app_label='runChart', model_name=model_name)
    if request.method == 'POST':
        form = CsvImportForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                contents = form.cleaned_data['csv_upload'].read().decode('utf-8-sig')
                records = csv.DictReader(StringIO(contents), delimiter=';')
                affected_runners = set()
                with transaction.atomic():
                    for line_number, row in enumerate(records, 2):
                        try:
                            if model_name == 'Runner':
                                fields = {k: v for k, v in row.items() if k in ('id', 'name', 'surname')}
                                fields['finished'] = (row.get('finished') or '').lower() in ('true', '1', 'yes')
                                runner = Runner.objects.create(**fields)
                                RunningLap.objects.create(
                                    runnerId=runner,
                                    startLapDate=race_datetime(settings.FIRST_DAY.time()),
                                    numberOfLaps=1,
                                )
                            elif model_name == 'RunningLap':
                                runner = Runner.objects.get(pk=int(row['runnerId']))
                                start = race_datetime(
                                    _import_clock(row['startLapDate']),
                                    _import_second_hour(row, 'startFold', 'startAfterChange'),
                                )
                                end_value = (row.get('endLapDate') or '').strip()
                                end = (race_datetime(
                                    _import_clock(end_value),
                                    _import_second_hour(row, 'endFold', 'endAfterChange'),
                                ) if end_value.lower() not in ('', 'none', 'null') else None)
                                if end is not None and end < start:
                                    raise ValueError('Koniec okrążenia jest przed jego rozpoczęciem.')
                                RunningLap.objects.create(
                                    runnerId=runner, startLapDate=start, endLapDate=end
                                )
                                affected_runners.add(runner.pk)
                            else:
                                raise ValueError(f'Nieobsługiwany model: {model_name}')
                        except (ValueError, KeyError, Runner.DoesNotExist) as exc:
                            raise ValueError(f'Wiersz {line_number}: {exc}') from exc
                    for runner_id in affected_runners:
                        renumber_runner_laps(runner_id)
                messages.success(request, 'Import CSV zakończony.')
            except (ValueError, UnicodeDecodeError) as exc:
                messages.error(request, f'Import nie powiódł się (bez częściowego zapisu): {exc}')
        else:
            messages.error(request, 'Nie wybrano prawidłowego pliku CSV.')
        return HttpResponseRedirect(reverse(f'admin:runChart_{model_name.lower()}_changelist'))
    return render(request, 'admin/csvFile_upload.html', {'form': CsvImportForm()})


@admin.register(Runner)
class RunnerAdmin(admin.ModelAdmin):
    change_list_template = 'admin/runChart/Runner/change_list.html'
    list_display = ('id', 'name', 'surname', 'finished')
    list_filter = ('id', 'name', 'surname', 'finished')
    search_fields = ('id', 'name', 'surname')
    ordering = ('id', 'name', 'surname', 'finished')

    def get_urls(self):
        return [path('upload-csvFile/', self.admin_site.admin_view(self.upload_csvFile))] + super().get_urls()

    @staticmethod
    def upload_csvFile(request):
        return upload_csvFileUniversal(request, 'Runner')


class RunningLapForm(forms.ModelForm):
    startLapTime = forms.TimeField(widget=widgets.AdminTimeWidget, label='Godzina rozpoczęcia')
    startAfterChange = forms.BooleanField(
        required=False, label='Rozpoczęcie: druga 02:00–02:59 (po zmianie czasu)'
    )
    endLapTime = forms.TimeField(
        widget=widgets.AdminTimeWidget, label='Godzina zakończenia', required=False
    )
    endAfterChange = forms.BooleanField(
        required=False, label='Zakończenie: druga 02:00–02:59 (po zmianie czasu)'
    )

    class Meta:
        model = RunningLap
        fields = ('runnerId',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            start = timezone.localtime(self.instance.startLapDate)
            self.fields['startLapTime'].initial = start.strftime('%H:%M:%S')
            self.fields['startAfterChange'].initial = bool(start.fold)
            if self.instance.endLapDate:
                end = timezone.localtime(self.instance.endLapDate)
                self.fields['endLapTime'].initial = end.strftime('%H:%M:%S')
                self.fields['endAfterChange'].initial = bool(end.fold)
        else:
            now = timezone.localtime()
            self.fields['startLapTime'].initial = now.strftime('%H:%M:%S')
            self.fields['startAfterChange'].initial = bool(now.fold)

    def clean(self):
        cleaned = super().clean()
        start_time = cleaned.get('startLapTime')
        end_time = cleaned.get('endLapTime')
        if start_time is None:
            return cleaned
        try:
            start = race_datetime(start_time, cleaned.get('startAfterChange', False))
            end = race_datetime(end_time, cleaned.get('endAfterChange', False))
        except ValueError as exc:
            raise forms.ValidationError(str(exc)) from exc
        if end is not None and end < start:
            self.add_error('endLapTime', 'Godzina zakończenia poprzedza rozpoczęcie okrążenia.')
        cleaned['resolved_start'] = start
        cleaned['resolved_end'] = end
        return cleaned


@admin.register(RunningLap)
class RunningLapAdmin(admin.ModelAdmin):
    change_list_template = 'admin/runChart/RunningLap/change_list.html'
    form = RunningLapForm
    list_display = ('runnerId', 'startCustomizedDate', 'endCustomizedDate', 'numberOfLaps')
    ordering = ('endLapDate', 'startLapDate', 'numberOfLaps', 'runnerId')
    list_filter = ('runnerId', 'runnerId__name', 'runnerId__surname', 'startLapDate', 'endLapDate', 'numberOfLaps')
    search_fields = ('runnerId__id', 'runnerId__name', 'runnerId__surname', 'numberOfLaps')
    fields = ('runnerId', 'startLapTime', 'startAfterChange', 'endLapTime', 'endAfterChange')

    @staticmethod
    @admin.display(description='Czas rozpoczęcia okrążenia', ordering='startLapDate')
    def startCustomizedDate(obj):
        return local_clock_label(obj.startLapDate, with_day=True)

    @staticmethod
    @admin.display(description='Czas zakończenia okrążenia', ordering='endLapDate')
    def endCustomizedDate(obj):
        return local_clock_label(obj.endLapDate, with_day=True) if obj.endLapDate else '—'

    def save_model(self, request, obj, form, change):
        old_runner_id = None
        if change and obj.pk:
            old_runner_id = RunningLap.objects.filter(pk=obj.pk).values_list('runnerId_id', flat=True).first()
        obj.startLapDate = form.cleaned_data['resolved_start']
        obj.endLapDate = form.cleaned_data['resolved_end']
        super().save_model(request, obj, form, change)
        renumber_runner_laps(obj.runnerId_id)
        if old_runner_id and old_runner_id != obj.runnerId_id:
            renumber_runner_laps(old_runner_id)

    def delete_model(self, request, obj):
        runner_id = obj.runnerId_id
        super().delete_model(request, obj)
        renumber_runner_laps(runner_id)

    def delete_queryset(self, request, queryset):
        runner_ids = set(queryset.values_list('runnerId_id', flat=True))
        super().delete_queryset(request, queryset)
        for runner_id in runner_ids:
            renumber_runner_laps(runner_id)

    def get_search_results(self, request, queryset, search_term):
        queryset, may_have_duplicates = super().get_search_results(
            request, queryset, search_term
        )
        if search_term:
            # Preserve the old search-by-datetime behavior of this admin screen.
            found = []
            for lap in RunningLap.objects.all().only('pk', 'startLapDate', 'endLapDate'):
                local_start = timezone.localtime(lap.startLapDate)
                local_end = timezone.localtime(lap.endLapDate) if lap.endLapDate else None
                if search_term in str(local_start) or (local_end and search_term in str(local_end)):
                    found.append(lap.pk)
            queryset = queryset | RunningLap.objects.filter(pk__in=found)
        return queryset, may_have_duplicates

    def get_urls(self):
        return [path('upload-csvFile/', self.admin_site.admin_view(self.upload_csvFile))] + super().get_urls()

    @staticmethod
    def upload_csvFile(request):
        return upload_csvFileUniversal(request, 'RunningLap')
