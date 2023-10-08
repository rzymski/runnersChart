from django import forms
from django.contrib.admin.widgets import AdminTimeWidget, AdminDateWidget, AdminSplitDateTime

class runTimeForm(forms.Form):
    name_input = forms.CharField(max_length=128)
    int_input = forms.IntegerField(min_value=0, max_value=10)
    date_input = forms.DateField(widget=AdminDateWidget, label="date")
    time_input = forms.TimeField(widget=AdminTimeWidget, label="time")

# class timeForm(forms.Form):
    #time_input = forms.TimeField(widget=AdminTimeWidget, label="time")
class nameForm(forms.Form):
    name_input = forms.CharField(max_length=128)


class MyForm(forms.Form):
    name_field = forms.CharField()
    int_field = forms.IntegerField()
    time_input = forms.TimeField(widget=AdminTimeWidget, label="time")
    # time_input = forms.TimeField()
    # class Meta:
    #     widgets = {
    #         'time_input': widgets.AdminTimeWidget(format='%H:%M')
    #     }

# forms.py
from django import forms

class ExampleListForm(forms.Form):
    def __init__(self, example_list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for item in example_list:
            self.fields[f'checkbox_{item}'] = forms.BooleanField(required=False, label=str(item))
