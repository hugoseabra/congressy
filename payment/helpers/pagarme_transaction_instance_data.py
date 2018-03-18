import os
import uuid
from decimal import Decimal

import absoluteuri
from django.conf import settings

from partner import constants as partner_constants
from payment.helpers.calculator import Calculator
from gatheros_event.models import Organization
from payment.exception import TransactionError

CONGRESSY_RECIPIENT_ID = settings.PAGARME_RECIPIENT_ID


class PagarmeTransactionInstanceData:
    # @TODO add international phone number capability

    def __init__(self, subscription, extra_data, event):

        self.subscription = subscription
        self.lot = subscription.lot
        self.person = subscription.person
        self.extra_data = extra_data
        self.event = event

        self._set_amount()
        self._set_organization()
        self._check_lot()
        self._set_transaction_type()
        self._set_installments()

        self.calculator = Calculator(
            int(self.installments),
            int(self.lot.num_install_interest_absortion)
        )

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
                    "unit_price": self.as_payment_format(self.amount),
                    "quantity": 1,
                    "tangible": False
                }
            ],

            "metadata": {
                "evento": self.event.name,
                "inscricao": str(self.subscription.pk)
            },

            "amount": self.as_payment_format(self.amount),
            "price": self.as_payment_format(self.amount),

            "split_rules": self._create_split_rules(),
        }

        if self.transaction_type == 'credit_card':
            transaction_data['payment_method'] = 'credit_card'
            transaction_data['card_hash'] = self.extra_data['card_hash']

            if self.subscription.lot.allow_installment is True \
                    and self.extra_data.get('installments') \
                    and int(self.extra_data.get('installments')) > 1:
                transaction_data['installments'] = \
                    int(self.extra_data.get('installments'))

        if self.transaction_type == 'boleto':
            transaction_data['installments'] = ''
            transaction_data['payment_method'] = 'boleto'

        # Estabelecer uma referência de qual o estado sistema houve a transação
        environment_version = os.getenv('ENVIRONMENT_VERSION')

        if environment_version:
            transaction_data['metadata']['system'] = {
                'version': environment_version,
                'enviroment': 'production'
            }

        return transaction_data

    @staticmethod
    def as_decimal(value):
        # Contexto de contrução de números decimais
        return round(Decimal(value), 2)

    @staticmethod
    def as_payment_format(value):
        value = str(round(value, 2))
        v_split = value.split('.')
        value = v_split[0]
        cents = v_split[1] if len(v_split) == 2 else ''
        return str(value + cents)

    def _set_amount(self):
        # Setado no _create_split_rules()
        self.liquid_amount = 0

        if self.extra_data.get('amount'):
            self.amount = \
                round(Decimal(self.extra_data.get('amount')), 2) / 100
        else:
            raise TransactionError(
                message="Transação sem valor."
            )

    def _check_lot(self):
        if int(self.lot.pk) != int(self.extra_data.get('lot')):
            raise TransactionError(
                message="Inscrição não pertence ao lote informado."
            )

    def _set_installments(self):
        self.installments = 1

        if self.transaction_type == 'credit_card' \
                and self.lot.allow_installment is True \
                and self.extra_data.get('installments') \
                and int(self.extra_data.get('installments')) > 1:
            self.installments = int(self.extra_data.get('installments'))

    def _set_organization(self):
        if 'organization' not in self.extra_data:
            raise TransactionError(message="No organization")
        self.organization = Organization.objects.get(
            pk=self.extra_data['organization'])

        if not self.organization.bank_account_id:
            raise TransactionError(message="Organization has no bank account")

    def _set_transaction_type(self):

        allowed_payment_methods = ['boleto', 'credit_card']

        if 'transaction_type' not in self.extra_data:
            raise TransactionError(
                message='Nenhum tipo de transação informado.'
            )

        if self.extra_data['transaction_type'] not in allowed_payment_methods:
            raise TransactionError(message='Tipo de transação não permitido.')

        self.transaction_type = self.extra_data['transaction_type']

    def _create_split_rules(self):
        """
        Contsroi as regras de split da transação.
        :param amount:
            Valor padronizado conforme exigido pelo Pagar.me, ou seja, os
            centavos são junto com o valor principal, sem separação de vingula.
        :return:
        """
        org_percent = self.as_decimal(
            (100 - float(self.event.congressy_percent)) / 100
        )

        # Com transferência, o valor da transaçaõ está maior do que o valor do
        # lote.
        #
        # O organizador sempre receberá o valor normal
        # do lote, pois a transação já está com as taxas que estão a cargo
        # do participante pagá-las.
        if self.subscription.lot.transfer_tax is True:
            # Valor da transação deve ser maior do que o valor do lote.
            assert self.amount > self.as_decimal(self.lot.price)

            # Se há parcelamento, verificar se o organizador irá assumir
            # juros de parcelas a partir de uma quantidade de parcelas.
            absorb_num_installment = self.lot.num_install_interest_absortion

            # se não há aborção de juros
            if not absorb_num_installment:
                organization_amount = self.as_decimal(self.lot.price)
            else:
                # Se há absorção, ver se o número de parcelas da transação
                # está dentre as parcelas assumids
                if self.installments <= absorb_num_installment:
                    # juros de parcelas
                    interest_price = \
                        self.calculator.get_installment_interest(
                            self.amount,
                            self.installments
                        )

                    # adiciona valor de juros assumidas à parte da organização
                    organization_amount = self.as_decimal(
                        self.lot.price - interest_price
                    )
                else:
                    organization_amount = self.as_decimal(self.lot.price)

        # Caso contrário, o organizador pagará receberá o valor padrão
        # subtraído das taxas da Congressy, já que não há taxas no valor do
        # lote a ser processado na transação.
        else:
            organization_amount = self.calculator.get_receiver_amount(
                self.lot.price,
                org_percent,
                self.installments
            )

        # Congressy receberá o restante
        congressy_amount = self.amount - organization_amount

        # Valor líquido da congressy direto do valor do lote.
        congressy_amount_liquid = self.lot.price * self.as_decimal(
            float(self.event.congressy_percent) / 100
        )

        # Se o valor é menor do que o mínimo configurado, o mínimo assume.
        minimum = self.as_decimal(settings.CONGRESSY_MINIMUM_AMOUNT)
        if congressy_amount < minimum:
            congressy_amount = minimum
            organization_amount = self.as_decimal(self.amount - minimum)

        # Verifica se há parceiros
        partners = self.event.partner_contracts.filter(
            partner__status=partner_constants.ACTIVE,
            partner__approved=True
        )

        partners_amount = 0
        partner_rules = []
        for contract in partners:
            percent_decimal = Decimal(contract.partner_plan.percent) / 100
            # O parceiro ganha em cima do valor liquido da Congressy.
            part_amount = self.as_decimal(
                congressy_amount_liquid * percent_decimal
            )
            partners_amount += part_amount
            partner_rules.append({
                "recipient_id": contract.partner.bank_account.recipient_id,
                "amount": self.as_payment_format(part_amount),
                "liable": True,
                "charge_processing_fee": False
            })

        congressy_rule = {
            "recipient_id": CONGRESSY_RECIPIENT_ID,
            "amount": self.as_payment_format(congressy_amount - partners_amount),
            "liable": True,
            "charge_processing_fee": True,
            "charge_remainder_fee": True
        }

        if settings.DEBUG is True and \
                hasattr(settings, 'PAGARME_TEST_RECIPIENT_ID'):
            org_recipient_id = settings.PAGARME_TEST_RECIPIENT_ID
        else:
            org_recipient_id = self.organization.recipient_id

        self.liquid_amount = organization_amount

        organization_rule = {
            "recipient_id": org_recipient_id,
            "amount": self.as_payment_format(organization_amount),
            "liable": True,
            "charge_processing_fee": False
        }

        split_rules = [congressy_rule, organization_rule]

        for partner_rule in partner_rules:
            split_rules.append(partner_rule)

        return split_rules
