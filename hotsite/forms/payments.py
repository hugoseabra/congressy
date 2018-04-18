"""
    Formulário usado para pegar os dados de pagamento
"""

import json

from django import forms
from django.core import serializers
from django.db import transaction
from django.forms import ValidationError

from gatheros_subscription.models import Lot, \
    Subscription
from payment.exception import TransactionError
from payment.helpers import PagarmeTransactionInstanceData
from payment.tasks import create_pagarme_transaction


class PaymentForm(forms.Form):
    installments = forms.IntegerField(
        widget=forms.HiddenInput(),
        required=False,
    )

    amount = forms.IntegerField(
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
        widget=forms.HiddenInput(),
        required=False,
    )

    def __init__(self, **kwargs):

        self.lot_instance = kwargs.get('initial').get('choosen_lot')
        self.event = kwargs.get('initial').get('event')

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

        lot_obj_as_json = serializers.serialize('json', [self.lot_instance, ])
        json_obj = json.loads(lot_obj_as_json)
        json_obj = json_obj[0]
        json_obj = json_obj['fields']

        del json_obj['exhibition_code']
        del json_obj['private']

        lot_obj_as_json = json.dumps(json_obj)

        self.fields['lot_as_json'].initial = lot_obj_as_json

    def clean(self):

        cleaned_data = super().clean()

        subscription = None

        try:
            subscription = Subscription.objects.get(
                person=self.storage.person,
                event=self.event
            )
        except Subscription.DoesNotExist:
            subscription = Subscription(
                person=self.storage.person,
                event=self.event,
                created_by=self.request.user.id
            )

        try:
            with transaction.atomic():
                # Insere ou edita lote
                subscription.lot = self.lot_instance
                subscription.save()
                self.storage.subscription = subscription

                transaction_data = PagarmeTransactionInstanceData(
                    subscription=subscription,
                    extra_data=cleaned_data,
                    event=self.event
                )

                create_pagarme_transaction(
                    transaction_data=transaction_data,
                    subscription=subscription
                )

        except TransactionError as e:
            error_dict = {
                'No transaction type': \
                    'Por favor escolher uma forma de pagamento.',
                'Transaction type not allowed': \
                    'Forma de pagamento não permitida.',
                'Organization has no bank account': \
                    'Organização não está podendo receber pagamentos no'
                    ' momento.',
                'No organization': 'Evento não possui organizador.',
            }
            if e.message in error_dict:
                e.message = error_dict[e.message]

            raise ValidationError({'transaction': e.message})

        return cleaned_data
