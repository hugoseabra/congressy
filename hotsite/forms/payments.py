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

    lot_as_json = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
    )

    products_as_json = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
    )

    def __init__(self, **kwargs):

        self.lot_instance = kwargs.get('initial').get('choosen_lot')
        self.event = kwargs.get('initial').get('event')
        self.person = kwargs.get('initial').get('person')
        self.products = kwargs.get('initial').get('optional_products')

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

        product_json = []

        if self.products and len(self.products) > 0:
            for product in self.products:
                product_json.append(
                    self.create_product_json(product))

        self.fields['products_as_json'].initial = json.dumps(product_json)

    # @TODO not DRY, fix
    def create_product_json(self, product):

        remove_fields = [
            'lot_category',
            'created_by',
            'modified_by',
            'created',
            'modified',
            'release_days',
            'optional_type',
            'quantity',
            'date_end_sub',
            'published',
        ]

        product.price = self.get_calculated_price(product.price,
                                                  self.lot_instance)

        product_obj_as_json = serializers.serialize('json', [product, ])
        product_obj = json.loads(product_obj_as_json)
        product_obj = product_obj[0]
        product_obj = product_obj['fields']

        for field in remove_fields:
            del product_obj[field]

        return product_obj

    # @TODO not DRY, fix
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
