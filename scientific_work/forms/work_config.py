from django import forms

from core.forms.widgets import SplitDateTimeWidget
from scientific_work.models import WorkConfig


class WorkConfigForm(forms.ModelForm):
    class Meta:
        model = WorkConfig
        fields = (
            'event',
            'date_start',
            'date_end',
            'presenting_type',
        )

    def __init__(self, *args, **kwargs):
        super(WorkConfigForm, self).__init__(*args, **kwargs)
        self.fields['date_start'].widget = SplitDateTimeWidget()
        self.fields['date_end'].widget = SplitDateTimeWidget()
        self.fields['event'].widget = forms.HiddenInput()

        for key in self.fields:
            self.fields[key].required = False
