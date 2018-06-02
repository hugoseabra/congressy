import os
import uuid
from decimal import Decimal

import absoluteuri
from django.conf import settings

from payment.exception import TransactionError
from payment.helpers.calculator import Calculator
from payment.helpers.payment_helpers import (
    amount_as_decimal,
    decimal_processable_amount,
    get_opened_boleto_transactions,
    is_boleto_allowed,
)
from payment.models import Transaction
from payment.receiver_subscribers import (
    ReceiverPublisher,
    ReceiverSubscriber,
)

CONGRESSY_RECIPIENT_ID = settings.PAGARME_RECIPIENT_ID


class PagarmeDataBuilder:
    # @TODO add international phone number capability

    def __init__(self, debt, transaction_type, card_hash=None):

        self.transaction_id = uuid.uuid4()
        self.debt = debt
        self.subscription = debt.subscription
        self.lot = self.subscription.lot
        self.event = self.lot.event
        self.person = self.subscription.person

        self.transaction_type = transaction_type
        self.card_hash = card_hash
        self._check_transaction_type()

        self.organization = self.event.organization
        if not self.organization.bank_account_id:
            raise TransactionError(
                message='Organização não está podendo receber pagamentos no'
                        ' momento.'
            )

        self.calculator = Calculator(
            self.debt.installments,
            int(self.lot.num_install_interest_absortion)
        )

    def build(self):
        def clear_string(string):
            string = string \
                .replace('.', '') \
                .replace('-', '') \
                .replace('/', '') \
                .replace('(', '') \
                .replace(')', '') \
                .replace(' ', '')

            return string

        postback_url = absoluteuri.reverse(
            'api:payment:payment_postback_url',
            kwargs={'uidb64': self.transaction_id}
        )

        data = {
            "api_key": settings.PAGARME_API_KEY,
            "postback_url": postback_url,
            "customer": {
                "external_id": str(self.subscription.pk),
                "name": self.person.name,
                "type": "individual",
                "country": "br",
                "email": self.person.email,
                "documents": [
                    {
                        "type": "cpf",
                        "number": self.person.cpf,
                    }
                ],
                "phone_numbers": ["+55" + clear_string(self.person.phone)],
                "birthday": self.person.birth_date.strftime('%Y-%m-%d'),
            },
            "billing": {
                "name": self.person.name,
                "address": {
                    "country": "br",
                    "state": self.person.city.uf.lower(),
                    "city": self.person.city.name.lower().capitalize(),
                    "neighborhood": self.person.village,
                    "street": self.person.street,
                    "street_number": str(self.person.number),
                    "zipcode": self.person.zip_code
                }
            },
            "items": [
                {
                    "id": str(self.event.pk),
                    "title": self.event.name,
                    "unit_price": self.as_payment_format(self.debt.amount),
                    "quantity": 1,
                    "tangible": False
                }
            ],
            "amount": self.as_payment_format(self.debt.amount),
            "price": self.as_payment_format(self.debt.amount),
            "payment_method": self.transaction_type,
            "installments": self.debt.installments,
            "metadata": {
                "lote": '{} (#{})'.format(
                    self.subscription.lot.name,
                    self.subscription.lot.pk
                ),
                "subscription": '{} (#{})'.format(
                    self.subscription.count,
                    self.subscription.pk
                ),
                "inscricao": str(self.subscription.pk)
            },
            "split_rules": self._create_split_rules(),
        }

        if self.transaction_type == Transaction.CREDIT_CARD:
            data['card_hash'] = self.card_hash

        # Estabelecer uma referência de qual o estado sistema houve a transação
        environment_version = os.getenv('ENVIRONMENT_VERSION')
        if environment_version:
            data['metadata']['system'] = {
                'version': environment_version,
                'enviroment': 'production'
            }

        return data

    @staticmethod
    def as_decimal(value):
        # Contexto de contrução de números decimais
        return amount_as_decimal(value)

    @staticmethod
    def as_payment_format(value):
        return decimal_processable_amount(value)

    def _check_transaction_type(self):
        if not self.transaction_type:
            raise TransactionError('Nenhum tipo de transação informado.')

        is_boleto = self.transaction_type == Transaction.BOLETO
        open_boleto_queryset = \
            get_opened_boleto_transactions(self.subscription)

        # se o evento permite boleto e se a inscrição não possui boletos
        # em aberto (não-vencidos)
        bolleto_allowed = is_boleto_allowed(
            self.event
        ) is True and open_boleto_queryset.count() == 0

        if is_boleto_allowed is False:
            raise TransactionError('Pagamento com boleto não permitido.')

        is_credit_card = self.transaction_type == Transaction.CREDIT_CARD
        if is_credit_card and not self.card_hash:
            raise TransactionError('O hash do cartão não foi encontrado.')

    def _create_split_rules(self):
        """
        Contsroi as regras de split da transação.
        :param amount:
            Valor padronizado conforme exigido pelo Pagar.me, ou seja, os
            centavos são junto com o valor principal, sem separação de vingula.
        :return:
        """

        subscriber = ReceiverSubscriber()
        publisher = ReceiverPublisher(
            receiver_subscriber=subscriber,
            subscription=self.debt.subscription,
            amount=self.debt.amount,
            installments=self.debt.installments,
        )

        # Por enquanto, receivers somente de inscrições
        publisher.create_and_publish_subscription()

        split_rules = []
        for id, receiver in subscriber.receivers.items():
            split_rules.append({
                "recipient_id": id,
                "amount": self.as_payment_format(receiver.amount),
                "liable": True,
                "charge_processing_fee": \
                    receiver.processing_fee_responsible is True
            })

        return split_rules
