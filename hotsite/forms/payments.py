"""
    Formulário usado para pegar os dados de pagamento
"""

from django import forms
from django.core import serializers
from gatheros_subscription.models import Lot
import json


class PaymentForm(forms.Form):
    installments = forms.IntegerField(
        widget=forms.HiddenInput()
    )

    amount = forms.IntegerField(
        widget=forms.HiddenInput()
    )

    lot = forms.IntegerField(
        widget=forms.HiddenInput()
    )

    card_hash = forms.IntegerField(
        widget=forms.HiddenInput(),
        required=False,
    )

    transaction_type = forms.CharField(
        widget=forms.HiddenInput()
    )

    lot_as_json = forms.CharField(
        widget=forms.HiddenInput()
    )

    def __init__(self, **kwargs):

        self.lot = kwargs.get('initial').get('lot')
        self.event = kwargs.get('initial').get('event')

        if not isinstance(self.lot, Lot):
            try:
                self.lot = Lot.objects.get(pk=self.lot, event=self.event)
            except Lot.DoesNotExist:
                message = 'Não foi possivel resgatar um Lote ' \
                          'a partir das referencias: lot<{}> e evento<{}>.' \
                    .format(self.lot, self.event)
                raise TypeError(message)

        super().__init__(**kwargs)

        lot_obj_as_json = serializers.serialize('json', [self.lot, ])
        json_obj = json.loads(lot_obj_as_json)
        json_obj = json_obj[0]
        json_obj = json_obj['fields']

        del json_obj['exhibition_code']
        del json_obj['private']

        lot_obj_as_json = json.dumps(json_obj)

        self.fields['lot_as_json'].initial = lot_obj_as_json
        self.fields['lot'].initial = self.lot.pk
