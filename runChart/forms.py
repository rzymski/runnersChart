from django import forms
from django.contrib.admin.widgets import AdminTimeWidget, AdminDateWidget, AdminSplitDateTime


class timeForm(forms.Form):
    start_time_input = forms.TimeField(widget=AdminTimeWidget, required=False)
    end_time_input = forms.TimeField(widget=AdminTimeWidget, required=False)

class MyTimeForm(forms.Form):
    time_input = forms.TimeField(widget=AdminTimeWidget, label="mainTime", required=False)

# forms.py
from django import forms

class ExampleListForm(forms.Form):
    def __init__(self, example_list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for item in example_list:
            self.fields[f'checkbox_{item}'] = forms.BooleanField(required=False, label=str(item))
