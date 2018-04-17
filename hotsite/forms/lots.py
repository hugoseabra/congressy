"""
    Formulário usado para selecionar o lote do evento.
"""

from datetime import datetime

from django import forms

from gatheros_subscription.models import Lot


class LotsForm(forms.Form):

    event = None

    current_step = forms.IntegerField(
        widget=forms.HiddenInput(),
        initial=1
    )

    next_step = forms.IntegerField(
        widget=forms.HiddenInput(),
        required=False,
        initial=2,
    )

    coupon_code = forms.CharField(
        max_length=15,
        required=False,
        label="Código de Cupom"
    )

    def __init__(self, event, post_data=None, **kwargs):

        self.event = event

        if post_data:
            kwargs.update({'initial': post_data})

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
        self.order_fields(['lots', 'coupon_code', 'next_step'])



