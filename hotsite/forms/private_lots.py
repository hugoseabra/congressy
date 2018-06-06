"""
    Formulário usado para selecionar o lote do evento.
"""

from datetime import datetime

from django import forms

from gatheros_subscription.models import Lot


class PrivateLotForm(forms.Form):
    lots = forms.ChoiceField(
        required=False,
        label='lote',
        widget=forms.HiddenInput(),
    )

    def __init__(self, event, code, **kwargs):
        self.event = event

        lot = None

        if code:
            try:
                lot = Lot.objects.get(exhibition_code=code.upper())
            except Lot.DoesNotExist:
                pass

        super().__init__(**kwargs)

        self.fields['lots'].choices = self.get_lot_choices()

        if lot:
            self.fields['lots'].initial = lot.pk

    def get_lot_choices(self):
        now = datetime.now()
        lots = Lot.objects.filter(event=self.event,
                                  active=True,
                                  date_start__lte=now,
                                  date_end__gte=now)

        return [
            (lot.id, lot.display_publicly)
            for lot in lots
            if lot.status == Lot.LOT_STATUS_RUNNING
        ]
