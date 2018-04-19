"""
    Formulário usado para selecionar o lote do evento.
"""

from datetime import datetime

from django import forms

from gatheros_subscription.models import Lot


class LotsForm(forms.Form):

    def __init__(self, **kwargs):

        self.event = kwargs.get('initial').get('event')
        super().__init__(**kwargs)

        self.fields['lots'] = forms.ModelChoiceField(
            queryset=Lot.objects.filter(event=self.event,
                                        date_start__lte=datetime.now(),
                                        date_end__gte=datetime.now(),
                                        private=False,
                                        ),
            empty_label="- Selecione -",
            required=True
        )
