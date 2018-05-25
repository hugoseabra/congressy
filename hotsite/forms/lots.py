"""
    Formulário usado para selecionar o lote do evento.
"""

from datetime import datetime

from django import forms
from django.forms import ModelChoiceField

from gatheros_subscription.models import Lot


class LotFormModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        if obj.price and obj.price > 0:
            return "{} - R$ {}".format(obj.name, obj.display_publicly)

        return "{}".format(obj.name)


class LotsForm(forms.Form):
    def __init__(self, event, **kwargs):
        self.event = event
        super().__init__(**kwargs)

        self.fields['lots'] = LotFormModelChoiceField(
            queryset=Lot.objects.filter(event=self.event,
                                        active=True,
                                        date_start__lte=datetime.now(),
                                        date_end__gte=datetime.now()),
            required=True,
            label='lote',
        )
        self.fields['lots'].choices = self.get_public_lot_choices()

    def get_public_lot_choices(self):
        public_lots = Lot.objects.filter(event=self.event,
                                         active=True,
                                         date_start__lte=datetime.now(),
                                         date_end__gte=datetime.now(),
                                         private=False)

        return [
            (lot.id, lot.display_publicly)
            for lot in public_lots
        ]
