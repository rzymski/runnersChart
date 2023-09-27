from django import forms
from django.contrib.admin.widgets import AdminTimeWidget, AdminDateWidget, AdminSplitDateTime

class runTimeForm(forms.Form):
    name_input = forms.CharField(max_length=128)
    int_input = forms.IntegerField(min_value=0, max_value=10)
    date_input = forms.DateField(widget=AdminDateWidget, label="date")
    time_input = forms.TimeField(widget=AdminTimeWidget, label="time")
