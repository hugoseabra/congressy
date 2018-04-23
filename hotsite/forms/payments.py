"""
    Formulário usado para pegar os dados de pagamento
"""

import json

from django import forms
from django.core import serializers

from gatheros_subscription.models import Lot


class PaymentForm(forms.Form):
    installments = forms.IntegerField(
        widget=forms.HiddenInput(),
        required=False,
    )

    amount = forms.IntegerField(
        widget=forms.HiddenInput(),
        required=True,
    )

    card_hash = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
    )

    transaction_type = forms.CharField(
        widget=forms.HiddenInput(),
        required=True,
    )

    lot_as_json = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
    )

    def __init__(self, **kwargs):

        self.lot_instance = kwargs.get('initial').get('choosen_lot')
        self.event = kwargs.get('initial').get('event')
        self.person = kwargs.get('initial').get('person')

        if not isinstance(self.lot_instance, Lot):
            try:
                self.lot_instance = Lot.objects.get(pk=self.lot_instance,
                                                    event=self.event)
            except Lot.DoesNotExist:
                message = 'Não foi possivel resgatar um Lote ' \
                          'a partir das referencias: lot<{}> e evento<{}>.' \
                    .format(self.lot_instance, self.event)
                raise TypeError(message)

        super().__init__(**kwargs)

        lot = self.lot_instance
        lot.price = lot.get_calculated_price()

        lot_obj_as_json = serializers.serialize('json', [lot, ])
        json_obj = json.loads(lot_obj_as_json)
        json_obj = json_obj[0]
        json_obj = json_obj['fields']

        del json_obj['exhibition_code']
        del json_obj['private']

        lot_obj_as_json = json.dumps(json_obj)

        self.fields['lot_as_json'].initial = lot_obj_as_json