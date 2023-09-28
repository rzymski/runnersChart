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
#Admin
# login : admin
# password : admin

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
                print(value)
                if value.lower() == 'none' or value.lower() == 'null' or value.lower() == '':
                    obj_dict[header] = None
                elif header == "runnerId":
                    obj_dict[header] = Runner.objects.get(id=value)
                elif header == "startLapDate":
                    start_lap_time_obj = datetime.strptime(value, "%H:%M").time()
                    if start_lap_time_obj >= time(21, 30):
                        start_lap_date_obj = timezone.make_aware(datetime(2023, 10, 21, start_lap_time_obj.hour, start_lap_time_obj.minute))
                    else:
                        start_lap_date_obj = timezone.make_aware(datetime(2023, 10, 22, start_lap_time_obj.hour, start_lap_time_obj.minute))
                    obj_dict[header] = start_lap_date_obj
                elif header == "endLapDate":
                    end_lap_time_obj = datetime.strptime(value, "%H:%M").time()
                    if end_lap_time_obj >= time(21, 30):
                        end_lap_date_obj = timezone.make_aware(datetime(2023, 10, 21, end_lap_time_obj.hour, end_lap_time_obj.minute))
                    else:
                        end_lap_date_obj = timezone.make_aware(datetime(2023, 10, 22, end_lap_time_obj.hour, end_lap_time_obj.minute))
                    obj_dict[header] = end_lap_date_obj
                else:
                    obj_dict[header] = value
            if model_name == "RunningLap":
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
    list_display = ('id', 'name', 'surname')
    list_filter = ('id', 'name', 'surname')
    search_fields = ('id', 'name', 'surname')
    ordering = ('id', 'name', 'surname')

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [path('upload-csvFile/', self.upload_csvFile), ]
        return new_urls + urls
    def upload_csvFile(self, request):
        return upload_csvFileUniversal(request, "Runner")


from django.contrib.admin import widgets
class RunningLapForm(forms.ModelForm):
    class Meta:
        model = RunningLap
        fields = '__all__'

    startLapTime = forms.TimeField(widget=widgets.AdminTimeWidget, label="Czas rozpoczecia okrazenia")
    endLapTime = forms.TimeField(widget=widgets.AdminTimeWidget, label="Czas zakonczenia okrazenia", required=False)

@admin.register(RunningLap)
class RunningLapAdmin(admin.ModelAdmin):
    form = RunningLapForm
    # list_display = ('runnerId', 'startCustomizedDate', 'endCustomizedDate', 'numberOfLaps')
    list_display = ('runnerId', 'startLapDate', 'endLapDate', 'numberOfLaps')
    ordering = ('endLapDate', 'numberOfLaps', 'runnerId')
    list_filter = ('runnerId', 'endLapDate', 'numberOfLaps')
    search_fields = ('runnerId', 'endLapDate', 'numberOfLaps')
    exclude = ('numberOfLaps', 'startLapDate', 'endLapDate')
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
            t = time(obj.endLapDate.hour, obj.endLapDate.minute)
            dt = datetime.combine(datetime.today(), t)
            dt += timedelta(hours=2)
        endLapTimeValue = dt.time() if obj is not None and obj.endLapDate is not None else time(datetime.now().hour, datetime.now().minute, datetime.now().second)
        if obj is not None and obj.startLapDate is not None:
            t2 = time(obj.startLapDate.hour, obj.startLapDate.minute)
            dt2 = datetime.combine(datetime.today(), t2)
            dt2 += timedelta(hours=2)
        startLapTimeValue = dt2.time() if obj is not None and obj.startLapDate is not None else time(datetime.now().hour, datetime.now().minute, datetime.now().second)
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
                obj.startLapDate = timezone.make_aware(datetime(2023, 10, 21, startLapTime.hour, startLapTime.minute))
            else:
                obj.startLapDate = timezone.make_aware(datetime(2023, 10, 22, startLapTime.hour, startLapTime.minute))
            endLapTime = form.cleaned_data.get('endLapTime')
            if endLapTime is not None:
                if endLapTime >= time(21, 30):
                    obj.endLapDate = timezone.make_aware(datetime(2023, 10, 21, endLapTime.hour, endLapTime.minute))
                else:
                    obj.endLapDate = timezone.make_aware(datetime(2023, 10, 22, endLapTime.hour, endLapTime.minute))
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

    def startCustomizedDate(self, obj):
        timezone.activate('Europe/Warsaw')
        formatedDate = timezone.localtime(obj.startLapDate).strftime('%d października %H:%M')
        timezone.deactivate()
        return formatedDate
    startCustomizedDate.short_description = 'Data rozpoczecia okrazenia biegu'
    def endCustomizedDate(self, obj):
        if obj.endLapDate is None:
            return '_________________________'
        timezone.activate('Europe/Warsaw')
        formatedDate = timezone.localtime(obj.endLapDate).strftime('%d października %H:%M')
        timezone.deactivate()
        return formatedDate
    endCustomizedDate.short_description = 'Data zakonczenia okrazenia biegu'

    def countLap(self, runner_id, start_lap_date):
        query = Q(runnerId=runner_id, startLapDate__lt=start_lap_date)
        number = RunningLap.objects.filter(query).count() + 1
        return number

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [path('upload-csvFile/', self.upload_csvFile), ]
        return new_urls + urls
    def upload_csvFile(self, request):
        return upload_csvFileUniversal(request, "RunningLap")