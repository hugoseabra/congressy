"""
    Formulário usado para pegar os dados de pagamento
"""

import json
import logging
from copy import copy

from django import forms
from django.core import serializers
from django.db.transaction import atomic

from payment.exception import (
    TransactionApiError,
    TransactionDataError,
    TransactionError,
    TransactionMisconfiguredError,
)
from payment.helpers import (
    PagarmeDataBuilder,
    payment_helpers,
)
from payment.tasks import create_pagarme_transaction

LOGGER = logging.getLogger(__name__)


class PaymentForm(forms.Form):
    transaction_type = forms.CharField(
        widget=forms.HiddenInput(),
        required=True,
    )

    installments = forms.IntegerField(
        widget=forms.HiddenInput(),
        required=False,
    )

    installment_part = forms.IntegerField(
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

    lot_as_json = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
    )

    def __init__(self, subscription, selected_ticket, **kwargs):

        self.subscription = subscription
        self.event = subscription.event
        self.person = subscription.person
        self.ticket_instance = selected_ticket

        self.subscription_debt_form = None
        self.product_debt_forms = list()
        self.service_debt_forms = list()

        # Caso a inscrição exista e o lote for diferente, altera o lote.
        self.subscription.ticket_lot = self.ticket_instance.current_lot

        super().__init__(**kwargs)

        lot_obj_as_json = serializers.serialize(
            'json',
            [self.ticket_instance.current_lot, ]
        )
        json_obj = json.loads(lot_obj_as_json)
        json_obj = json_obj[0]
        json_obj = json_obj['fields']

        lot_obj_as_json = json.dumps(json_obj)

        self.fields['lot_as_json'].initial = lot_obj_as_json

    def clean_transaction_type(self):
        transaction_type = self.cleaned_data['transaction_type']

        boleto_allowed = payment_helpers.is_boleto_allowed(self.event)
        if transaction_type == 'boleto' and boleto_allowed is False:
            raise forms.ValidationError(
                'Transação com boleto não é permitida.'
            )

        return transaction_type

    def clean_installments(self):
        installments = self.cleaned_data['installments']
        if not installments or int(installments) <= 1:
            installments = 1

        if installments > 10:
            installments = 10

        return int(installments)

    def clean_installment_part(self):
        part = self.cleaned_data.get('installment_part', 1)

        if not part:
            part = 1

        if part < 1:
            part = 1

        if part > self.cleaned_data['installments']:
            raise forms.ValidationError(
                'Número de parcela excede a quantidade parcelamento.'
            )

        return part

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        return payment_helpers.amount_as_decimal(amount)

    def clean_card_hash(self):
        card_hash = self.cleaned_data['card_hash']
        return card_hash or None

    def save(self):
        with atomic():
            self.subscription.save()

            ticket = self.subscription.ticket

            try:
                # Construção de dados para transaçao do Pagarme
                builder = PagarmeDataBuilder(subscription=self.subscription)

                builder.add_debt(
                    debt_type='sub',
                    debt_pk=str(self.subscription.pk),
                    title='Inc: {}, Evento: {}, Ingresso: {}'.format(
                        self.subscription.code,
                        self.event.name,
                        self.subscription.ticket.name,
                    ),
                    amount=ticket.get_subscriber_price(),
                    liquid_amount=ticket.get_liquid_amount(),
                )

                products = self.subscription.subscription_products.filter(
                    optional__liquid_price__gt=0
                )
                for sub_prod in products:
                    prod = sub_prod.optional

                    builder.add_debt(
                        debt_type='addon-prod',
                        debt_pk=str(prod.pk),
                        title='Opcional: {} ({})'.format(prod.name, prod.pk),
                        amount=prod.price,
                        liquid_amount=prod.liquid_price,
                    )

                services = self.subscription.subscription_services.filter(
                    optional__liquid_price__gt=0
                )
                for sub_serv in services:
                    serv = sub_serv.optional

                    builder.add_debt(
                        debt_type='addon-serv',
                        debt_pk=str(serv.pk),
                        title='Atividade extra: {} ({})'.format(serv.name,
                                                                serv.pk),
                        amount=serv.price,
                        liquid_amount=serv.liquid_price,
                    )

                installment_part = self.cleaned_data.get('installment_part', 1)
                trans_type = self.cleaned_data.get('transaction_type')

                # Cria transação.
                return create_pagarme_transaction(
                    subscription=self.subscription,
                    data=builder.build(
                        amount=self.cleaned_data.get('amount'),
                        transaction_type=trans_type,
                        installments=self.cleaned_data.get('installments'),
                        card_hash=self.cleaned_data.get('card_hash'),
                    ),
                    installments=self.cleaned_data.get('installments'),
                    installment_part=installment_part,
                )

            except TransactionDataError as e:
                LOGGER.error(
                    'Um erro aconteceu enquanto se tentava construir os dados'
                    ' de uma transação. Detalhes: {}'.format(e)
                )
                raise TransactionError(
                    'Erro interno ao realizar transação. A equipe técnica já'
                    ' foi informada e este erro será resolvido dentro de'
                    ' alguns minutos.'
                )

            except TransactionMisconfiguredError as e:
                LOGGER.warning(
                    'O evento "{}" não pode realizar transações não pode'
                    ' completar uma transação para a inscrição "{}".'
                    ' Detalhes: {}'.format(
                        '{} ({})'.format(
                            self.subscription.event.name,
                            self.subscription.event.pk,
                        ),
                        '{} ({})'.format(
                            self.subscription.person.name,
                            self.subscription.pk,
                        ),
                        str(e)
                    )
                )
                raise TransactionError(
                    'O evento não pode realizar transações. Por favor,'
                    ' entre em contato com o organizador do evento informando'
                    ' sobre o ocorrido.'
                )

            except TransactionApiError as e:
                LOGGER.error(
                    'Um erro aconteceu enquanto se tentava realizar uma'
                    ' transação. Detalhes: {}'.format(e)
                )
                raise TransactionError(str(e))

            except TransactionError as e:
                raise e
