from django import forms

from csv_importer.models import CSVImportFile
from gatheros_event.models import Event


class CSVForm(forms.ModelForm):
    event = None

    class Meta:
        model = CSVImportFile
        fields = [
            'event',
            'csv_file',
            'separator',
            'delimiter',
            'encoding',
        ]

        widgets = {
            'event': forms.HiddenInput(),
        }

    def __init__(self, event_pk, *args, **kwargs):
        self.event = Event.objects.get(pk=event_pk)
        super().__init__(*args, **kwargs)
        self.fields['event'].inital = self.event.pk
