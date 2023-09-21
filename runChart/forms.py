from django import forms
from .models import RunningLap
from datetime import datetime
from django.contrib.admin.widgets import AdminDateWidget, AdminTimeWidget, AdminSplitDateTime

class TimePickerWidget(forms.TextInput):
    template_name = 'partials/timepicker.html'


class RunningLapForm(forms.ModelForm):
    class Meta:
        model = RunningLap
        fields = '__all__'
        widgets = {
            'runnerId': forms.Select(attrs={'class': 'form-control'}),
            'endLapTime': forms.TimeInput(attrs={'class': 'form-control'}),
            'endLapDate': forms.HiddenInput(),
            'numberOfLaps': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['endLapDate'].initial = datetime(2023, 10, 22, 22, 0)
        self.fields['numberOfLaps'].initial = 0
