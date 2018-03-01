import os
import uuid
from decimal import Decimal

import absoluteuri
from django.conf import settings

from gatheros_event.models import Organization
from partner.models import PartnerContract
from payment.exception import TransactionError

CONGRESSY_RECIPIENT_ID = settings.PAGARME_RECIPIENT_ID


class PagarmeTransactionInstanceData:
    # @TODO add international phone number capability

    def __init__(self, subscription, extra_data, event):

        self.subscription = subscription
        self.person = subscription.person
        self.extra_data = extra_data
        self.event = event

        self.lot = subscription.lot

        if int(self.lot.pk) != int(self.extra_data.get('lot')):
            raise TransactionError(
                message="Inscrição não pertence ao lote informado."
            )

        self._get_organization()
        self._get_transaction_type()

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

    def get_data(self):

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

        transaction_data = {

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
                    "unit_price": self.as_payment_format(
                        self.lot.get_calculated_price()
                    ),
                    "quantity": 1,
                    "tangible": False
                }
            ],

            "split_rules": self._create_split_rules(),
            "metadata": {
                "evento": self.event.name,
                "inscricao": str(self.subscription.pk)
            },

            "amount": self.as_payment_format(self.lot.get_calculated_price()),
            "price": self.as_payment_format(self.lot.get_calculated_price())
        }

        # if self.subscription.lot.allow_installment is True \
        #         and self.extra_data.get('installments'):



        # Estabelecer uma referência de qual o estado sistema houve a transação
        environment_version = os.getenv('ENVIRONMENT_VERSION')

        if environment_version:
            transaction_data['metadata']['system'] = {
                'version': environment_version,
                'enviroment': 'production'
            }

        if self.transaction_type == 'credit_card':
            transaction_data['payment_method'] = 'credit_card'
            transaction_data['card_hash'] = self.extra_data['card_hash']

        if self.transaction_type == 'boleto':
            transaction_data['payment_method'] = 'boleto'

        return transaction_data

    def _create_partner_rule(self, partner, amount):
        return {
            "recipient_id": partner,
            "amount": self.as_payment_format(amount),
            "liable": True,
            "charge_processing_fee": True,
            "charge_remainder_fee": True
        }

    def _get_partner_organization(self, partner):

        partner_organization = None

        try:
            partner_organization = Organization.objects.get(
                name=partner.person.name)
        except Organization.DoesNotExist:
            pass

        return partner_organization

    def _create_split_rules(self):
        """
        Contsroi as regras de split da transação.
        :param amount:
            Valor padronizado conforme exigido pelo Pagar.me, ou seja, os
            centavos são junto com o valor principal, sem separação de vingula.
        :return:
        """

        # Preço padrão, sem cálculos de transferências de taxas.
        amount = self.lot.price

        # O cálculo do montante da congressy será sempre em cima do preço
        # padrão.
        congressy_percent = settings.CONGRESSY_PLAN_PERCENT_10
        congressy_amount = round(
            self.lot.price * (self.as_decimal(congressy_percent) / 100),
            2
        )

        # Se o valor é menor do que o mínimo configurado, o mínimo assume.
        minimum = self.as_decimal(settings.CONGRESSY_MINIMUM_AMOUNT)
        if congressy_amount < minimum:
            congressy_amount = minimum

        # Com transferência, o organizador sempre receberá o valor padrão
        # o valor das taxas já está inserido no valor do lote a ser processado
        # na transação.
        if self.subscription.lot.transfer_tax is True:
            organization_amount = amount

        # Caso contrário, o organizador receberá o valor padrão subtraído das
        # taxas da Congressy, já que não há taxas no valor do lote a ser
        # processado na transação.
        else:
            organization_amount = self.as_decimal(amount - congressy_amount)

        all_partner_contracts = PartnerContract.objects.filter(event=self.event)

        for contract in all_partner_contracts:
            pass




        congressy_rule = {
            "recipient_id": CONGRESSY_RECIPIENT_ID,
            "amount": self.as_payment_format(congressy_amount),
            "liable": True,
            "charge_processing_fee": True,
            "charge_remainder_fee": True
        }

        if settings.DEBUG is True and \
                hasattr(settings, 'PAGARME_TEST_RECIPIENT_ID'):
            org_recipient_id = settings.PAGARME_TEST_RECIPIENT_ID
        else:
            org_recipient_id = self.organization.recipient_id

        organization_rule = {
            "recipient_id": org_recipient_id,
            "amount": self.as_payment_format(organization_amount),
            "liable": True,
            "charge_processing_fee": False
        }

        return [congressy_rule, organization_rule]

    @staticmethod
    def as_decimal(value):
        # Contexto de contrução de números decimais
        return round(Decimal(value), 2)

    @staticmethod
    def as_payment_format(value):
        return str(round(value, 2)).replace('.', '')