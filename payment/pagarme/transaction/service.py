import logging
from datetime import datetime
from decimal import Decimal
from pprint import pprint

import pagarme
from django.conf import settings
from django.db.transaction import atomic

from gatheros_subscription.models import Subscription
from installment.models import Part
from payment.exception import TransactionApiError
from payment.helpers import payment_helpers
from payment.models import Transaction, TransactionStatus, SplitRule
from payment.pagarme_sdk.transaction import get_split_rules
from payment.payable.updater import update_payables
from .transaction import PagarmeTransaction


def notify_error(message, extra_data=None):
    logger = logging.getLogger(__name__)
    logger.error(message, extra=extra_data)


pagarme.authentication_key(settings.PAGARME_API_KEY)

congressy_id = settings.PAGARME_RECIPIENT_ID


class PagarmeTransactionCreatorMixin:
    @staticmethod
    def create_pagarme_transaction(data):

        try:
            return pagarme.transaction.create(data)

        except Exception as e:

            pprint(e)
            pprint(data)

            errors_msg = []
            if hasattr(e, 'args'):
                errors = [errs for errs in e.args]
                for error in errors[0]:
                    if isinstance(error, dict):
                        errors_msg.append('{}: {}'.format(
                            error.get('parameter_name'),
                            error.get('message'),
                        ))
                    else:
                        errors_msg.append(error)
            else:
                errors_msg.append(e)

            msg = 'Pagar.me: erro de' \
                  ' transação: {}'.format(";".join(errors_msg))

            notify_error(message=msg, extra_data=data)
            raise TransactionApiError(
                'Algo deu errado com a comunicação com o provedor de'
                ' pagamento.'
            )

    @staticmethod
    def create_pagarme_split_rules(transaction_id: str):

        try:
            return get_split_rules(transaction_id)

        except Exception as e:

            pprint(e)
            pprint(transaction_id)

            errors_msg = []
            if hasattr(e, 'args'):
                errors = [errs for errs in e.args]
                for error in errors[0]:
                    if isinstance(error, dict):
                        errors_msg.append('{}: {}'.format(
                            error.get('parameter_name'),
                            error.get('message'),
                        ))
                    else:
                        errors_msg.append(error)
            else:
                errors_msg.append(e)

            msg = 'Pagar.me: erro de' \
                  ' transação: {}'.format(";".join(errors_msg))

            notify_error(message=msg,
                         extra_data={'transaction_id': transaction_id})

            raise TransactionApiError(
                'Algo deu errado com a comunicação com o provedor de'
                ' pagamento.'
            )


class PagarmeAPISubscriptionService(PagarmeTransactionCreatorMixin):
    def __init__(self,
                 pagarme_transaction: PagarmeTransaction,
                 subscription: Subscription):

        self.pagarme_transaction = pagarme_transaction

        self.subscription = subscription
        self.lot = self.subscription.audience_lot
        self.audience_category = self.lot.audience_category

        self.transaction = None
        self.transaction_status = None

    def create_transaction(self,
                           num_installment_part: int,
                           installment_interests_amount: Decimal,
                           contract_part: Part = None):

        """
        Montante da transação pode ser:

        SE BOLETO:
        - TOTAL: se parcelamento for igual a 1, pois não o pagamento é
                 integral;
        - PARCIAL: se parcelamento for mais do que 1, pois o montante
                   transacionado equivale apenas à parcela de pagamento;

        SE CARTÃO:
        - TOTAL: independente do parcelamento, pois o parcelamento de cartão
                 é controlado pelo provedor de pagamento e, por sua vez, pela
                 bandeira do cartão;
        """

        amount = self.pagarme_transaction.amount
        installments = self.pagarme_transaction.installments

        if contract_part is not None:
            # Se há parcela de pagamento, o valor da parcela é o valor que
            # que consta no registro da parcela.
            installment_amount = contract_part.amount

            # O montante a transacionar é o valor da parcela
            assert round(amount, 2) == round(installment_amount, 2), \
                'O valor da parcela não é o valor a ser transacionado.' \
                ' Transação: {}. Parcela: {}.'.format(
                    round(amount, 2),
                    round(installment_amount, 2),
                )

        elif self.pagarme_transaction.is_credit_card() and installments > 1:
            # Se há parcelamento no cartão, o valor da parcela é definido
            # pela transação em si.
            installment_amount = amount / installments

        else:
            installment_amount = 0

        with atomic():
            self._create_congressy_transaction(
                num_installment_part=num_installment_part,
                installment_amount=installment_amount,
                installment_interests_amount=installment_interests_amount,
                contract_part=contract_part,
            )

            self._increment_congressy_transaction(
                self.create_pagarme_transaction(dict(self.pagarme_transaction))
            )

            self.transaction.save()
            self.transaction_status.save()

        # outro atômico para persistir transação mesmo se algo acontecer com
        # a criação de regras de split.
        with atomic():
            split_rules_trx = self.create_pagarme_split_rules(
                self.transaction.pagarme_id
            )

            for sr in split_rules_trx:
                fee_resp = sr['charge_processing_fee']
                amount = payment_helpers.amount_as_decimal(str(sr['amount']))

                created = datetime.strptime(
                    sr['date_created'],
                    "%Y-%m-%dT%H:%M:%S.%fZ"
                )

                split_rule = SplitRule.objects.create(
                    transaction=self.transaction,
                    pagarme_id=sr['id'],
                    is_congressy=fee_resp is True,
                    charge_processing_fee=fee_resp is True,
                    amount=amount,
                    recipient_id=sr['recipient_id'],
                    created=created,
                )

                update_payables(split_rule)

        if settings.DEBUG is True:
            print('Transaction ID: {} - R$ {}'.format(
                self.transaction.pk,
                round(self.transaction.amount, 2),
            ))
            print('Pagarme Transaction ID: {}'.format(
                self.transaction.pagarme_transaction_id
            ))

        return self.transaction

    def _create_congressy_transaction(self,
                                      num_installment_part: int,
                                      installment_amount: Decimal,
                                      installment_interests_amount: Decimal,
                                      contract_part: Part = None):

        pt = self.pagarme_transaction

        amount = pt.amount if contract_part is None else contract_part.amount

        discounted_amount = pt.discounted_amount
        if contract_part:
            pt.discounted_amount = contract_part.discount_amount

        liquid_amount = \
            pt.amount if contract_part is None else contract_part.liquid_amount

        if contract_part:
            installment_interests_amount = contract_part.interests_amount

        self.transaction = Transaction(
            uuid=pt.transaction_id,
            subscription=self.subscription,
            type=pt.payment_method,
            amount=amount,
            lot_price=self.lot.price,
            liquid_amount=liquid_amount,
            installments=pt.installments,
            installment_part=num_installment_part,
            installment_amount=installment_amount,
            installment_interests_amount=installment_interests_amount,
            discounted_amount=discounted_amount,
        )

        if contract_part:
            self.transaction.part = contract_part

        return self.transaction

    def _increment_congressy_transaction(self, response_data):

        self.transaction.pagarme_transaction_id = response_data['id']
        self.transaction.status = response_data['status']
        self.transaction.date_created = response_data['date_created']

        if self.pagarme_transaction.is_boleto():
            boleto_exp_date = response_data.get('boleto_expiration_date')
            if boleto_exp_date:
                self.transaction.boleto_expiration_date = datetime.strptime(
                    boleto_exp_date,
                    "%Y-%m-%dT%H:%M:%S.%fZ"
                ).date()

        if self.pagarme_transaction.is_credit_card():
            card = response_data['card']
            self.transaction.credit_card_brand = card['card_brand']
            self.transaction.credit_card_holder = card['holder_name']
            self.transaction.credit_card_first_digits = card['first_digits']
            self.transaction.credit_card_last_digits = card['last_digits']

        self.transaction_status = TransactionStatus.objects.create(
            transaction=self.transaction,
            data=response_data,
            status=response_data['status'],
            date_created=response_data['date_created'],
        )
