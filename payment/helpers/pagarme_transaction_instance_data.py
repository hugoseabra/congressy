import os
import uuid
from decimal import Decimal, getcontext as decimal_context

import absoluteuri
from django.conf import settings

from gatheros_event.models import Organization
from payment.exception import TransactionError

CONGRESSY_RECIPIENT_ID = settings.PAGARME_RECIPIENT_ID


class PagarmeTransactionInstanceData:
    # @TODO add international phone number capability

    def __init__(self, subscription, extra_data, event):

        self.subscription = subscription
        self.person = subscription.person
        self.extra_data = extra_data
        self.event = event

        self._get_organization()
        self._get_transaction_type()
        self._parametrize_instance_data()

    def _get_organization(self):

        if 'organization' not in self.extra_data:
            raise TransactionError(message="No organization")
        self.organization = Organization.objects.get(
            pk=self.extra_data['organization'])

        if not self.organization.bank_account_id:
            raise TransactionError(message="Organization has no bank account")

    def _get_transaction_type(self):

        allowed_payment_methods = ['boleto', 'credit_card']

        if 'transaction_type' not in self.extra_data:
            raise TransactionError(message='No transaction type')

        if self.extra_data['transaction_type'] not in allowed_payment_methods:
            raise TransactionError(message='Transaction type not allowed')

        self.transaction_type = self.extra_data['transaction_type']

    def _parametrize_instance_data(self):

        # Chave única da transação.
        transaction_id = uuid.uuid4()

        postback_url = absoluteuri.reverse(
            'api:payment:payment_postback_url',
            kwargs={'uidb64': transaction_id}
        )

        def clear_string(string):
            string = string \
                .replace('.', '') \
                .replace('-', '') \
                .replace('/', '') \
                .replace('(', '') \
                .replace(')', '') \
                .replace(' ', '')

            return string

        self.transaction_instance_data = {

            "api_key": settings.PAGARME_API_KEY,

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

            "postback_url": postback_url,

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
                    "id": str(transaction_id),
                    "title": self.event.name,
                    "unit_price": self.extra_data['amount'],
                    "quantity": 1,
                    "tangible": False
                }
            ],

            "split_rules": self._create_split_rules(self.extra_data['amount']),
            "metadata": {
                "evento": self.event.name,
                "inscricao": str(self.subscription.pk)
            },

            "amount": self.extra_data['amount'],
            "price": self.extra_data['amount']
        }

        # Estabelecer uma referência de qual o estado sistema hovue a transação
        environment_version = os.getenv('ENVIRONMENT_VERSION')
        if environment_version:
            self.transaction_instance_data['metadata']['system'] = {
                'version': environment_version,
                'enviroment': 'production'
            }

        if self.transaction_type == 'credit_card':
            self.transaction_instance_data['payment_method'] = 'credit_card'
            self.transaction_instance_data['card_hash'] = \
                self.extra_data['card_hash']

        if self.transaction_type == 'boleto':
            self.transaction_instance_data['payment_method'] = 'boleto'

    def _create_split_rules(self, amount):
        """
        Contsroi as regras de split da transação.
        :param amount:
            Valor padronizado conforme exigido pelo Pagar.me, ou seja, os
            centavos são junto com o valor principal, sem separação de vingula.
        :return:
        """
        def as_decimal(value):
            # Contexto de contrução de números decimais
            return round(Decimal(value), 2)

        def as_payment_format(value):
            return str(value).replace('.', '')

        # Separar centavos
        size = len(str(amount))
        cents = str(amount)[-2] + str(amount)[-1]
        amount = '{}.{}'.format(amount[0:size - 2], cents)
        amount = as_decimal(amount)

        congressy_percent_as_decimal = as_decimal(
            settings.CONGRESSY_PLAN_PERCENT_10
        )
        congressy_amount = as_decimal(
            amount * (congressy_percent_as_decimal / 100)
        )

        # Se o valor é menor do que o mínimo configurado, o mínimo assume.
        minimum = as_decimal(settings.CONGRESSY_MINIMUM_AMOUNT)
        if congressy_amount < minimum:
            congressy_amount = minimum

        organization_amount = as_decimal(amount - congressy_amount)

        congressy_rule = {
            "recipient_id": CONGRESSY_RECIPIENT_ID,
            "amount": as_payment_format(congressy_amount),
            "liable": True,
            "charge_processing_fee": True,
            "charge_remainder_fee": True
        }

        organization_rule = {
            "recipient_id": self.organization.recipient_id,
            "amount": as_payment_format(organization_amount),
            "liable": True,
            "charge_processing_fee": False
        }

        return [congressy_rule, organization_rule]
