from django import forms

from gatheros_event.models import Event
from gatheros_subscription.models import Lot
from importer.models import CSVFileConfig


class CSVFileConfigForm(forms.ModelForm):
    event = None

    class Meta:
        model = CSVFileConfig
        fields = [
            'event',
            'separator',
            'delimiter',
            'encoding',
            'lot',
        ]

        widgets = {
            'event': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.event = self.get_event(kwargs)

        if self.event:
            self.fields['lot'].queryset = Lot.objects.filter(
                event=self.event
            )
        else:
            raise Exception(
                'Não foi possivel pegar uma referencia para buscar os lotes')

    @staticmethod
    def get_event(kwargs):

        initial = kwargs.get('initial')

        if initial:
            event_pk = initial['event']
            return Event.objects.get(pk=event_pk)

        instance = kwargs.get('instance')
        if instance:
            return instance.lot.event

        return None
