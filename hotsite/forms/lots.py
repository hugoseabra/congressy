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
            return "{} - R${}".format(obj.name, obj.price)

        return "{}".format(obj.name)


class LotsForm(forms.Form):

    def __init__(self, **kwargs):
        self.event = kwargs.get('initial').get('event')
        super().__init__(**kwargs)

        self.fields['lots'] = LotFormModelChoiceField(
            queryset=Lot.objects.filter(event=self.event,
                                        date_start__lte=datetime.now(),
                                        date_end__gte=datetime.now(),
                                        private=False),
            empty_label="- Selecione -",
            required=True,
            label='lote',
        )

        if self.is_bound:
            self.fields['lots'].queryset = Lot.objects.filter(event=self.event,
                                                              date_start__lte=datetime.now(),
                                                              date_end__gte=datetime.now())
