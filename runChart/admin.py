from django.contrib import admin
from django.apps import apps
from django.urls import path
from django import forms
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from .models import *
from django.shortcuts import render, redirect
from datetime import time, datetime, timedelta
from django.utils import timezone
from django.db.models import Q
from django.contrib.admin import widgets
from django.conf import settings

FIRST_DAY = settings.FIRST_DAY
SECOND_DAY = settings.SECOND_DAY


class CsvImportForm(forms.Form):
    csv_upload = forms.FileField()


def upload_csvFileUniversal(request, model_name):
    model = apps.get_model(app_label='runChart', model_name=model_name)
    if request.method == "POST":
        csv_file = request.FILES["csv_upload"]
        file_data = csv_file.read().decode("utf-8-sig")
        lines = file_data.strip().split('\n')
        headers = lines[0].strip().split(';')
        for line in lines[1:]:
            values = line.strip().split(';')
            obj_dict = {}
            for header, value in zip(headers, values):
                if value.lower() == 'none' or value.lower() == 'null' or value.lower() == '':
                    obj_dict[header] = None
                elif header == "runnerId":
                    obj_dict[header] = Runner.objects.get(id=value)
                elif header == "startLapDate":
                    start_lap_time_obj = datetime.strptime(value, "%H:%M").time()
                    if start_lap_time_obj >= time(21, 30):
                        start_lap_date_obj = timezone.make_aware(datetime(FIRST_DAY.year, FIRST_DAY.month, FIRST_DAY.day, start_lap_time_obj.hour, start_lap_time_obj.minute))
                    else:
                        start_lap_date_obj = timezone.make_aware(datetime(SECOND_DAY.year, SECOND_DAY.month, SECOND_DAY.day, start_lap_time_obj.hour, start_lap_time_obj.minute))
                    obj_dict[header] = start_lap_date_obj
                elif header == "endLapDate":
                    end_lap_time_obj = datetime.strptime(value, "%H:%M").time()
                    if end_lap_time_obj >= time(21, 30):
                        end_lap_date_obj = timezone.make_aware(datetime(FIRST_DAY.year, FIRST_DAY.month, FIRST_DAY.day, end_lap_time_obj.hour, end_lap_time_obj.minute))
                    else:
                        end_lap_date_obj = timezone.make_aware(datetime(SECOND_DAY.year, SECOND_DAY.month, SECOND_DAY.day, end_lap_time_obj.hour, end_lap_time_obj.minute))
                    obj_dict[header] = end_lap_date_obj
                else:
                    obj_dict[header] = value
            if model_name == "Runner":
                runner_instance = model(**obj_dict)
                runner_instance.save()
                # Tworzenie rekordu RunningLap dla każdego nowego biegacza
                RunningLap.objects.create(runnerId=runner_instance, startLapDate=timezone.make_aware(FIRST_DAY), numberOfLaps=1)
            elif model_name == "RunningLap":
                admin_instance = RunningLapAdmin(model, admin.site)
                admin_instance.save_model(request, model(**obj_dict), None, False)
            else:
                instance = model(**obj_dict)
                instance.save()

        url = reverse(f'admin:runChart_{model_name.lower()}_changelist')
        return HttpResponseRedirect(url)
    form = CsvImportForm()
    data = {"form": form}
    return render(request, "admin/csvFile_upload.html", data)


@admin.register(Runner)
class RunnerAdmin(admin.ModelAdmin):
    change_list_template = 'admin/runChart/Runner/change_list.html'
    list_display = ('id', 'name', 'surname', 'finished')
    list_filter = ('id', 'name', 'surname', 'finished')
    search_fields = ('id', 'name', 'surname')
    ordering = ('id', 'name', 'surname', 'finished')

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [path('upload-csvFile/', self.upload_csvFile), ]
        return new_urls + urls

    @staticmethod
    def upload_csvFile(request):
        return upload_csvFileUniversal(request, "Runner")


class RunningLapForm(forms.ModelForm):
    class Meta:
        model = RunningLap
        fields = '__all__'
    startLapTime = forms.TimeField(widget=widgets.AdminTimeWidget, label="Czas rozpoczecia okrazenia")
    endLapTime = forms.TimeField(widget=widgets.AdminTimeWidget, label="Czas zakonczenia okrazenia", required=False)


@admin.register(RunningLap)
class RunningLapAdmin(admin.ModelAdmin):
    change_list_template = 'admin/runChart/RunningLap/change_list.html'
    form = RunningLapForm
    list_display = ('runnerId', 'startCustomizedDate', 'endCustomizedDate', 'numberOfLaps')
    # list_display = ('runnerId', 'startLapDate', 'endLapDate', 'numberOfLaps')
    ordering = ('endLapDate', 'startLapDate', 'numberOfLaps', 'runnerId')
    list_filter = ('runnerId', 'runnerId__name', 'runnerId__surname', 'startLapDate', 'endLapDate', 'numberOfLaps')
    # search_fields = ('runnerId__id', 'runnerId__name', 'runnerId__surname', 'startLapDate', 'endLapDate', 'numberOfLaps')
    search_fields = ('runnerId__id', 'runnerId__name', 'runnerId__surname', 'numberOfLaps')
    exclude = ('numberOfLaps', 'startLapDate', 'endLapDate') #nie trzeba podawać przy dodawaniu nowego rekordu

    @staticmethod
    def getPolishMonthName(monthNumber):
        months = ["styczeń", "luty", "marzec", "kwiecień", "maj", "czerwiec", "lipiec", "sierpień", "wrzesień", "październik", "listopad", "grudzień"]
        return months[monthNumber-1]

    def startCustomizedDate(self, obj):
        timezone.activate('Europe/Warsaw')
        monthName = RunningLapAdmin.getPolishMonthName(timezone.localtime(obj.startLapDate).month)
        formatedDate = timezone.localtime(obj.startLapDate).strftime(f'%d {monthName} %H:%M')
        timezone.deactivate()
        return formatedDate
    startCustomizedDate.short_description = 'Czas rozpoczecia okrazenia'

    def endCustomizedDate(self, obj):
        if obj.endLapDate is None:
            return '_________________________'
        timezone.activate('Europe/Warsaw')
        monthName = RunningLapAdmin.getPolishMonthName(timezone.localtime(obj.endLapDate).month)
        formatedDate = timezone.localtime(obj.endLapDate).strftime(f'%d {monthName} %H:%M')
        timezone.deactivate()
        return formatedDate
    endCustomizedDate.short_description = 'Czas zakonczenia okrazenia'

    startCustomizedDate.admin_order_field = 'startLapDate'
    endCustomizedDate.admin_order_field = 'endLapDate'

    def delete_view(self, request, object_id, extra_context=None):
        if request.method == "POST":
            obj = self.get_object(request, object_id)
            runsAfter = RunningLap.objects.filter(
                runnerId=obj.runnerId,
                startLapDate__gt=obj.startLapDate)
            for run in runsAfter:
                run.numberOfLaps -= 1
                run.save()
            print(runsAfter)
        return super().delete_view(request, object_id, extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        if request.method == "POST":
            obj = self.get_object(request, object_id)
            runsAfter = RunningLap.objects.filter(
                runnerId=obj.runnerId,
                startLapDate__gt=obj.startLapDate)
            for run in runsAfter:
                run.numberOfLaps -= 1
                run.save()
        return super().change_view(request, object_id, form_url, extra_context)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj is not None and obj.endLapDate is not None:
            end_local_dt = timezone.localtime(obj.endLapDate)
            endLapTimeValue = end_local_dt.time()
        else:
            endLapTimeValue = timezone.localtime().time()
        if obj is not None and obj.startLapDate is not None:
            start_local_dt = timezone.localtime(obj.startLapDate)
            startLapTimeValue = start_local_dt.time()
        else:
            startLapTimeValue = timezone.localtime().time()
        recommended_values = {
            'startLapTime': startLapTimeValue,
            'endLapTime': endLapTimeValue,
        }
        for field_name, recommended_value in recommended_values.items():
            form.base_fields[field_name].widget.attrs['value'] = recommended_value
        return form

    def save_model(self, request, obj, form, change):
        if form is not None:
            startLapTime = form.cleaned_data.get('startLapTime')
            if startLapTime >= time(21, 30):
                obj.startLapDate = timezone.make_aware(datetime(FIRST_DAY.year, FIRST_DAY.month, FIRST_DAY.day, startLapTime.hour, startLapTime.minute))
            else:
                obj.startLapDate = timezone.make_aware(datetime(SECOND_DAY.year, SECOND_DAY.month, SECOND_DAY.day, startLapTime.hour, startLapTime.minute))
            endLapTime = form.cleaned_data.get('endLapTime')
            if endLapTime is not None:
                if endLapTime >= time(21, 30):
                    obj.endLapDate = timezone.make_aware(datetime(FIRST_DAY.year, FIRST_DAY.month, FIRST_DAY.day, endLapTime.hour, endLapTime.minute))
                else:
                    obj.endLapDate = timezone.make_aware(datetime(SECOND_DAY.year, SECOND_DAY.month, SECOND_DAY.day, endLapTime.hour, endLapTime.minute))
            else:
                obj.endLapDate = None
        super().save_model(request, obj, form, change)
        query = Q(runnerId=obj.runnerId, startLapDate__gt=obj.startLapDate)
        records_after = RunningLap.objects.filter(query)
        for record in records_after:
            record.numberOfLaps += 1
            record.save()
        obj.numberOfLaps = self.countLap(obj.runnerId, obj.startLapDate)
        obj.save()

    def get_search_results(self, request, queryset, search_term):
        queryset, may_have_duplicates = super().get_search_results(
            request,
            queryset,
            search_term,
        )
        if search_term != '':
            print(queryset)
            lapsWithDate = self.search_date(search_term)
            lapsWithDate_queryset = RunningLap.objects.filter(pk__in=[lap.pk for lap in lapsWithDate])
            print(lapsWithDate_queryset)
            queryset |= lapsWithDate_queryset
        return queryset, may_have_duplicates

    @staticmethod
    def search_date(search_term):
        laps = RunningLap.objects.all()
        lapsWithDate = []
        for lap in laps:
            timezone.activate('Europe/Warsaw')
            startD = timezone.localtime(lap.startLapDate)
            endD = timezone.localtime(lap.endLapDate) if lap.endLapDate else None
            if search_term in str(startD) or endD and search_term in str(endD):
                lapsWithDate.append(lap)
            timezone.deactivate()
        return lapsWithDate

    @staticmethod
    def countLap(runner_id, start_lap_date):
        query = Q(runnerId=runner_id, startLapDate__lt=start_lap_date)
        number = RunningLap.objects.filter(query).count() + 1
        return number

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [path('upload-csvFile/', self.upload_csvFile), ]
        return new_urls + urls

    @staticmethod
    def upload_csvFile(request):
        return upload_csvFileUniversal(request, "RunningLap")
