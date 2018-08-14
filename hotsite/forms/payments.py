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
from payment_debt.forms import Debt, DebtForm

LOGGER = logging.getLogger(__name__)


class DebtAlreadyPaid(Exception):
    """
    Quando uma inscrição não é possível de ser feito porque a inscrição já
    está paga.
    """
    pass


class PaymentForm(forms.Form):
    transaction_type = forms.CharField(
        widget=forms.HiddenInput(),
        required=True,
    )

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

    lot_as_json = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
    )

    def __init__(self, subscription, selected_lot, **kwargs):

        self.subscription = subscription
        self.event = subscription.event
        self.person = subscription.person
        self.lot_instance = selected_lot

        # Caso a inscrição exista e o lote for diferente, altera o lote.
        self.subscription.lot = self.lot_instance

        super().__init__(**kwargs)

        self.subscription_debt_form = self._create_subscription_debt_form()
        self.product_debt_forms = self._create_product_debt_forms()
        self.service_debt_forms = self._create_service_debt_forms()

        lot = copy(self.lot_instance)
        lot.price = lot.get_calculated_price()

        lot_obj_as_json = serializers.serialize('json', [lot, ])
        json_obj = json.loads(lot_obj_as_json)
        json_obj = json_obj[0]
        json_obj = json_obj['fields']

        del json_obj['exhibition_code']
        del json_obj['private']

        lot_obj_as_json = json.dumps(json_obj)

        self.fields['lot_as_json'].initial = lot_obj_as_json

    def clean_transaction_type(self):
        transaction_type = self.cleaned_data['transaction_type']

        boleto_allowed = payment_helpers.is_boleto_allowed(
            self.subscription.event
        )
        if transaction_type == 'boleto' and boleto_allowed is False:
            raise forms.ValidationError(
                'Transação com boleto não é permitida.'
            )

        return transaction_type

    def clean_installments(self):
        installments = self.cleaned_data['installments']
        if not installments or int(installments) <= 1:
            return 1

        return int(installments)

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        return payment_helpers.amount_as_decimal(amount)

    def clean_card_hash(self):
        card_hash = self.cleaned_data['card_hash']
        return card_hash or None

    def clean(self):
        cleaned_data = super().clean()

        # if self.subscription.free is True:
        #     raise forms.ValidationError(
        #         'Pagamentos não podem ser processados para inscrições'
        #         ' gratuitas.'
        #     )

        if not self.subscription_debt_form.is_valid():
            error_msgs = []
            for field, errs in self.subscription_debt_form.errors.items():
                error_msgs.append(str(errs))

            raise forms.ValidationError(
                'Dados de pendência inválidos: {}'.format("".join(error_msgs))
            )

        for debt_form in self.product_debt_forms:
            if not debt_form.is_valid():
                error_msgs = []
                for field, errs in debt_form.items():
                    error_msgs.append(str(errs))

                raise forms.ValidationError(
                    'Dados de pendência de opcionais inválidos:'
                    ' {}'.format("".join(error_msgs))
                )

        for debt_form in self.service_debt_forms:
            if not debt_form.is_valid():
                error_msgs = []
                for field, errs in debt_form.items():
                    error_msgs.append(str(errs))

                raise forms.ValidationError(
                    'Dados de pendência de atividades extras inválidos:'
                    ' {}'.format("".join(error_msgs))
                )

        return cleaned_data

    def save(self):
        with atomic():
            self.subscription.save()

            # Novo ou edição de pendência financeira
            sub_debt = self.subscription_debt_form.save()

            try:
                # Construção de dados para transaçao do Pagarme
                builder = PagarmeDataBuilder(subscription=self.subscription)

                builder.add_debt(sub_debt)

                for debt_form in self.service_debt_forms:
                    serv_debt = debt_form.save()
                    builder.add_debt(serv_debt)

                for debt_form in self.product_debt_forms:
                    prod_debt = debt_form.save()
                    builder.add_debt(prod_debt)

                # Cria transação.
                create_pagarme_transaction(
                    subscription=self.subscription,
                    data=builder.build(
                        amount=self.cleaned_data.get('amount'),
                        transaction_type=self.cleaned_data.get(
                            'transaction_type'
                        ),
                        installments=self.cleaned_data.get('installments'),
                        card_hash=self.cleaned_data.get('card_hash'),
                    )
                )

            except TransactionDataError as e:
                LOGGER.error(
                    'Um erro aconteceu enquanto se tentava construir os dados'
                    ' de uma transação. Detalhes: {}'.format(e)
                )
                raise TransactionError(
                    'Erro interno ao realizar transação. A equipe técnica já'
                    ' foi informa e este erro será resolvido dentro de alguns'
                    ' minutos.'
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

    def _create_subscription_debt_form(self):
        """ Cria formulário de pendência financeira de inscrição. """

        installments = self.data.get('payment-installments', 1) or 1

        debt_kwargs = {
            'subscription': self.subscription,
            'data': {
                'name': 'Inscrição: {} ({})'.format(
                    self.subscription.event.name,
                    self.subscription.pk,
                ),
                'item_id': str(self.subscription.pk),
                'amount': self.subscription.lot.get_calculated_price(),
                'installments': installments,
                'status': Debt.DEBT_STATUS_DEBT,
                'type': Debt.DEBT_TYPE_SUBSCRIPTION,
            }
        }

        try:
            debt = self.subscription.debts.get(
                type=Debt.DEBT_TYPE_SUBSCRIPTION,
                subscription=self.subscription,
                status=Debt.DEBT_STATUS_DEBT,
            )

            debt_kwargs['instance'] = debt

            # # Se é possível processar pendência, somente débito não estiver
            # # pago e não possuindo crédito.
            # debt_allowed = debt.paid is False and debt.has_credit is False
            #
            # if debt_allowed is False:
            #     # Pendência financeira já está paga ou com crédito.
            #     raise DebtAlreadyPaid(
            #         'Esta pendência já está paga. Não é necessário realizar'
            #         ' novo registro de pendência.'
            #     )

        except Debt.DoesNotExist:
            pass

        return DebtForm(**debt_kwargs)

    def _create_service_debt_forms(self):
        """ Cria formulário de pendência financeira de atividade extra. """

        services = self.subscription.subscription_services.all()

        service_forms = []
        for service in services:
            if not service.optional_price:
                continue

            debt_kwargs = {
                'subscription': self.subscription,
                'data': {
                    'name': 'Atividade extra: {} ({})'.format(
                        service.optional.name,
                        service.optional.pk,
                    ),
                    'item_id': str(service.optional.pk),
                    'amount': service.optional.price,
                    # parcelamento sempre 1
                    'installments': 1,
                    'status': Debt.DEBT_STATUS_DEBT,
                    'type': Debt.DEBT_TYPE_SERVICE,
                }
            }

            try:
                debt = self.subscription.debts.get(
                    type=Debt.DEBT_TYPE_SERVICE,
                    item_id=str(service.optional.pk),
                )

                debt_kwargs['instance'] = debt

            except Debt.DoesNotExist:
                pass

            service_forms.append(DebtForm(**debt_kwargs))

        return service_forms

    def _create_product_debt_forms(self):
        """ Cria formulário de pendência financeira de opcionais. """

        products = self.subscription.subscription_products.all()

        prod_forms = []
        for product in products:
            if not product.optional_price:
                continue

            debt_kwargs = {
                'subscription': self.subscription,
                'data': {
                    'name': 'Produto/Serviço: {} ({})'.format(
                        product.optional.name,
                        product.optional.pk,
                    ),
                    'item_id': str(product.optional.pk),
                    'amount': product.optional.price,
                    # parcelamento sempre 1
                    'installments': 1,
                    'status': Debt.DEBT_STATUS_DEBT,
                    'type': Debt.DEBT_TYPE_PRODUCT,
                }
            }

            try:
                debt = self.subscription.debts.get(
                    type=Debt.DEBT_TYPE_PRODUCT,
                    item_id=str(product.optional.pk),
                )

                debt_kwargs['instance'] = debt

            except Debt.DoesNotExist:
                pass

            prod_forms.append(DebtForm(**debt_kwargs))

        return prod_forms
