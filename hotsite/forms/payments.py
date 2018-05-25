"""
    Formulário usado para pegar os dados de pagamento
"""

import json
from decimal import Decimal

from django import forms
from django.conf import settings
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

    def __init__(self, chosen_lot, event, person, **kwargs):

        self.lot_instance = chosen_lot
        self.event = event
        self.person = person

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

    def get_calculated_price(self, price, lot):
        """
        Resgata o valor calculado do preço do opcional de acordo com as regras
        da Congressy.
        """
        if price is None:
            return 0

        minimum = Decimal(settings.CONGRESSY_MINIMUM_AMOUNT)
        congressy_plan_percent = \
            Decimal(self.event.congressy_percent) / 100

        congressy_amount = price * congressy_plan_percent
        if congressy_amount < minimum:
            congressy_amount = minimum

        if lot.transfer_tax is True:
            return round(price + congressy_amount, 2)

        return round(price, 2)
