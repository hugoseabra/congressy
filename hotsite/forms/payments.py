"""
    Formulário usado para pegar os dados de pagamento
"""

import json
from copy import copy

from django import forms
from django.core import serializers
from django.db.transaction import atomic

from gatheros_subscription.models import Lot
from payment.helpers import (
    PagarmeDataBuilder,
    payment_helpers,
)
from payment.tasks import create_pagarme_transaction
from payment_debt.forms import Debt, DebtForm


class DebtAlreadyPaid(Exception):
    """
    Quando uma inscrição não é possível de ser feito porque a inscrição já
    está paga.
    """
    pass


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

    def __init__(self, subscription, **kwargs):

        self.subscription = subscription
        self.event = subscription.event
        self.person = subscription.person

        self.lot_instance = kwargs.get('initial').get('choosen_lot')

        if not isinstance(self.lot_instance, Lot):
            try:
                self.lot_instance = Lot.objects.get(pk=self.lot_instance,
                                                    event=self.event)
            except Lot.DoesNotExist:
                message = 'Não foi possivel resgatar um Lote ' \
                          'a partir das referencias: lot<{}> e evento<{}>.' \
                    .format(self.lot_instance, self.event)
                raise TypeError(message)

        # Caso a inscrição exista e o lote for diferente, altera o lote.
        self.subscription.lot = self.lot_instance

        super().__init__(**kwargs)

        self.subscription_debt_form = self._create_subscription_debt_form()

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

    def clean(self):
        cleaned_data = super().clean()

        if self.subscription.free is True:
            raise forms.ValidationError(
                'Pagamentos não podem ser processados para inscrições'
                ' gratuitas.'
            )

        installments = int(cleaned_data['amount'])
        if not installments:
            cleaned_data['amount'] = 1

        cleaned_data['card_hash'] = cleaned_data['card_hash'] or None

        if not self.subscription_debt_form.is_valid():
            error_msgs = []
            for field, errs in self.subscription_debt_form.errors.items():
                error_msgs.append(str(errs))

            raise forms.ValidationError(
                'Dados de pendência inválidos: {}'.format("".join(error_msgs))
            )

        transaction_type = self.cleaned_data.get('transaction_type')
        boleto_allowed = payment_helpers.is_boleto_allowed(
            self.subscription.event
        )

        if transaction_type == 'boleto' and boleto_allowed is False:
            raise Validation('Transação com boleto não é permitida.')

        return cleaned_data

    def save(self):
        with atomic():
            self.subscription.save()

            # Novo ou edição de pendência financeira
            debt = self.subscription_debt_form.save()

            # Construção de dados para transaçao do Pagarme
            builder = PagarmeDataBuilder(
                debt=debt,
                transaction_type=self.cleaned_data.get('transaction_type'),
                card_hash=self.cleaned_data.get('card_hash') or None,
            )

            # Cria transação.
            create_pagarme_transaction(
                transaction_id=builder.transaction_id,
                debt=debt,
                data=builder.build()
            )

    def _create_subscription_debt_form(self):
        """ Cria formulário de pendência financeira. """

        installments = self.data.get('payment-installments', 1) or 1

        debt_kwargs = {
            'subscription': self.subscription,
            'data': {
                'amount': self.data.get('payment-amount'),
                'installments': installments,
                'status': Debt.DEBT_STATUS_DEBT,
                # por enquanto, só pendências de inscrição
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

            # Se é possível processar pendência, somente débito não estiver
            # pago e não possuindo crédito.
            debt_allowed = debt.paid is False and debt.has_credit is False

            if debt_allowed is False:
                # Pendência financeira já está paga ou com crédito.
                raise DebtAlreadyPaid(
                    'Esta inscrição já está paga. Não é necessário realizar'
                    ' novo registro de pagamento.'
                )

        except Debt.DoesNotExist:
            pass

        return DebtForm(**debt_kwargs)
