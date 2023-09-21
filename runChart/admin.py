from django.contrib import admin
from django.apps import apps
from django.urls import path
from django import forms
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from .models import *
from django.shortcuts import render, redirect
from datetime import time, datetime
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
                if value.lower() == 'none' or value.lower() == 'null' or value.lower() == '':
                    obj_dict[header] = None
                elif header == "runnerId":
                    obj_dict[header] = Runner.objects.get(id=value)
                elif header == "endLapTime":
                    end_lap_time_obj = datetime.strptime(value, "%H:%M").time()
                    obj_dict[header] = end_lap_time_obj
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

@admin.register(RunningLap)
class RunningLapAdmin(admin.ModelAdmin):
    list_display = ('runnerId', 'customizedDate', 'numberOfLaps')
    ordering = ('endLapDate', 'numberOfLaps', 'runnerId')
    list_filter = ('runnerId', 'endLapDate', 'numberOfLaps')
    search_fields = ('runnerId', 'endLapDate', 'numberOfLaps')
    # ordering = ('endLapTime', 'runnerId')
    # list_filter = ('runnerId', 'endLapTime')
    # search_fields = ('runnerId', 'endLapTime')

    exclude = ('numberOfLaps', 'endLapDate')
    def save_model(self, request, obj, form, change):
        obj.endLapDate = self.setDate(obj.endLapTime)
        obj.numberOfLaps = self.countLap(obj.runnerId, obj.endLapDate)
        super().save_model(request, obj, form, change)
        #check if not added new laps before some existing
        query = Q(runnerId=obj.runnerId, endLapDate__gt=obj.endLapDate)
        records_after = RunningLap.objects.filter(query)
        for record in records_after:
            record.numberOfLaps += 1
            record.save()

    def customizedDate(self, obj):
        timezone.activate('Europe/Warsaw')
        formatedDate = timezone.localtime(obj.endLapDate).strftime('%d października %H:%M')
        timezone.deactivate()
        return formatedDate
    customizedDate.short_description = 'Data zakonczenia okrazenia biegu'
    def setDate(self, endLapTime):
        if endLapTime > time(16, 0):
            return datetime(2023, 10, 21, endLapTime.hour, endLapTime.minute)
        else:
            return datetime(2023, 10, 22, endLapTime.hour, endLapTime.minute)
    def countLap(self, runner_id, end_lap_date):
        query = Q(runnerId=runner_id, endLapDate__lt=end_lap_date)
        number = RunningLap.objects.filter(query).count() + 1
        return number

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [path('upload-csvFile/', self.upload_csvFile), ]
        return new_urls + urls
    def upload_csvFile(self, request):
        return upload_csvFileUniversal(request, "RunningLap")