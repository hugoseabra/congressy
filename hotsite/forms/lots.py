"""
    Formulário usado para selecionar o lote do evento.
"""

from datetime import datetime

from django import forms

from gatheros_subscription.models import Lot


class LotsForm(forms.Form):
    event = None
    def __init__(self, **kwargs):

        self.event = self.event

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

    coupon_code = forms.CharField(
        max_length=15,
        required=False,
    )
