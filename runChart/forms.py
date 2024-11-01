from django import forms
from django.contrib.admin.widgets import AdminTimeWidget


class TimeForm(forms.Form):
    start_time_input = forms.TimeField(widget=AdminTimeWidget(), required=False)
    end_time_input = forms.TimeField(widget=AdminTimeWidget(), required=False)


class MyTimeForm(forms.Form):
    time_input = forms.TimeField(widget=AdminTimeWidget(), label="mainTime", required=False)
