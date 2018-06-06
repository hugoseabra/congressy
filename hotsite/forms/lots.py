"""
    Formulário usado para selecionar o lote do evento.
"""

from datetime import datetime

from django import forms

from gatheros_subscription.models import Lot


class LotsForm(forms.Form):
    lots = forms.ModelChoiceField(
        required=True,
        label='lote',
        queryset=Lot.objects.filter(active=True)
    )

    def __init__(self, event, **kwargs):
        self.event = event
        super().__init__(**kwargs)

        now = datetime.now()
        self.fields['lots'].queryset = self.fields['lots'].queryset.filter(
            event=self.event,
            date_start__lte=now,
            date_end__gte=now,
        )
        self.fields['lots'].choices = self.get_public_lot_choices()

    def get_public_lot_choices(self):
        public_lots = self.fields['lots'].queryset.filter(private=False)
        return [
            (lot.id, lot.display_publicly)
            for lot in public_lots
            if lot.status == Lot.LOT_STATUS_RUNNING
        ]
