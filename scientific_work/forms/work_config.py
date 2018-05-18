from django import forms

from core.forms.widgets import SplitDateTimeWidget
from scientific_work.models import WorkConfig


class WorkConfigForm(forms.ModelForm):

    event = None

    class Meta:
        model = WorkConfig
        fields = [
            'event',
            'date_start',
            'date_end',
            'presenting_type',
        ]

        widgets = {
            'date_start': SplitDateTimeWidget(),
            'date_end': SplitDateTimeWidget(),
            'event': forms.HiddenInput()
        }

    def __init__(self, *args, **kwargs):
        super(WorkConfigForm, self).__init__(*args, **kwargs)

        for key in self.fields:
            self.fields[key].required = False




