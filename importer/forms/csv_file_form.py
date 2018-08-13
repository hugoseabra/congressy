from django import forms

from importer.models import CSVFileConfig
from gatheros_event.models import Event
from gatheros_subscription.models import Lot


class CSVFileForm(forms.ModelForm):
    event = None

    class Meta:
        model = CSVFileConfig
        fields = [
            'event',
            'csv_file',
            'lot',
        ]

        widgets = {
            'event': forms.HiddenInput(),
        }

        labels = {
            'csv_file': 'Arquivo CSV:',
            'lot': 'Escolha um lote para importar as inscrições:',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        initial = kwargs.get('initial')

        if initial:
            event_pk = initial['event']
            self.event = Event.objects.get(pk=event_pk)
            self.fields['lot'].queryset = Lot.objects.filter(
                event=self.event
            )
