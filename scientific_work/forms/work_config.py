from django import forms

from core.forms.widgets import SplitDateTimeBootsrapWidget
from scientific_work.models import WorkConfig


class WorkConfigForm(forms.ModelForm):
    class Meta:
        model = WorkConfig
        fields = (
            'event',
            'date_start',
            'date_end',
            'presenting_type',
            'allow_unconfirmed_subscriptions',
        )

    def __init__(self, *args, **kwargs):
        super(WorkConfigForm, self).__init__(*args, **kwargs)
        self.fields['date_start'].widget = SplitDateTimeBootsrapWidget()
        self.fields['date_end'].widget = SplitDateTimeBootsrapWidget()
        self.fields['event'].widget = forms.HiddenInput()

        msg = 'Permitir submissão por inscrições não confirmadas.'
        self.fields['allow_unconfirmed_subscriptions'].help_text = msg

        for key in self.fields:
            self.fields[key].required = False
