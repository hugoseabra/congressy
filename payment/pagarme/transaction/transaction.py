import os
from datetime import date, datetime, timedelta
from decimal import Decimal

from payment.helpers.payment_helpers import as_payment_amount
from .billing import Billing
from .customer import Customer
from .item import Item
from .split_rule import SplitRule


class PagarmeTransaction:
    CREDIT_CARD = 'credit_card'
    BOLETO = 'boleto'

    def __init__(self,
                 transaction_id: str,
                 interests_amount: Decimal,
                 installments=1):

        self.transaction_id = transaction_id
        self.interests_amount = interests_amount
        self.installments = installments

        self.payment_method = None

        self.boleto_data = dict()
        self.credit_card_hash = None
        self.credit_card_data = dict()

        self.amount = Decimal(0)
        self.liquid_amount = Decimal(0)

        self.postback_url = None

        self.customer = None
        self.billing = None

        self.metadata = dict()
        self._set_default_metadata_items()

        self.items = list()
        self.split_rules = list()

        self.errors = dict()

    @property
    def original_amount(self):
        """
        Valor original sem juros inclusos.
        """
        return self.amount - self.interests_amount

    def is_valid(self):
        self._check_errors()
        return len(self.errors) == 0

    def is_boleto(self):
        return self.payment_method == self.BOLETO

    def is_credit_card(self):
        return self.payment_method == self.CREDIT_CARD

    def set_customer(self, customer: Customer):
        self.customer = customer

    def set_billing(self, billing: Billing):
        self.billing = billing

    def set_postaback_url(self, url):
        self.postback_url = url

    def add_item(self, item: Item):
        self.items.append(item)

        self.amount += item.unit_price
        self.liquid_amount += item.liquid_unit_price

    def add_split_rule(self, rule: SplitRule):
        self.split_rules.append(rule)

    def add_metadata(self, key, value):
        self.metadata[key] = value

    def set_boleto_data(self,
                        soft_descriptor: str,
                        boleto_instructions: str,
                        expiration_date: date = None, ):

        self.payment_method = self.BOLETO

        assert len(boleto_instructions) <= 255, \
            "boleto instructions {} > 255".format(
                len(boleto_instructions)
            )

        assert len(soft_descriptor) <= 13, \
            "soft_descriptor {} > 13".format(
                len(soft_descriptor)
            )

        self.boleto_data.update({'soft_descriptor': soft_descriptor,
                                 'boleto_instructions': boleto_instructions})

        if expiration_date:
            assert expiration_date >= datetime.now().date()

            # day_before = expiration_date - timedelta(days=1)

            self.boleto_data.update({
                'boleto_expiration_date': expiration_date.strftime('%Y-%m-%d'),
            })

    def set_as_credit_card_hash(self, card_hash: str):
        self.payment_method = self.BOLETO

        self.credit_card_hash = card_hash

    def set_as_credit_card_data(self,
                                card_number: str,
                                card_cvv: str,
                                card_expiration_date: str,
                                card_holder_name: str):

        self.payment_method = self.CREDIT_CARD
        self.credit_card_data = {
            'card_number': card_number,
            'card_cvv': card_cvv,
            'card_expiration_date': card_expiration_date,
            'card_holder_name': card_holder_name,
        }

    def __iter__(self):

        if self.is_valid() is False:
            msg = 'PagarmeTransaction não está válido:'

            for k, v in self.errors.items():
                msg += ' {}: {}.'.format(k, v)

            raise Exception(msg)

        iters = {
            'transaction_id': self.transaction_id,
            'amount': as_payment_amount(round(self.amount, 2)),
            'price': as_payment_amount(round(self.amount, 2)),
            'liquid_amount': as_payment_amount(self.liquid_amount),
            'interests_amount': as_payment_amount(self.interests_amount),
            'payment_method': self.payment_method,
            'installments': self.installments,
            'metadata': self.metadata,
            'items': [dict(item) for item in self.items],
            'customer': dict(self.customer),
            'billing': dict(self.billing),
            'split_rules': [dict(rule) for rule in self.split_rules],
        }

        if self.postback_url:
            iters.update({'postback_url': self.postback_url})

        if self.payment_method == self.BOLETO:
            assert self.boleto_data is not None
            iters.update(self.boleto_data)

        elif self.payment_method == self.CREDIT_CARD:
            if self.credit_card_hash:
                iters.update({'card_hash': self.credit_card_hash})
            else:
                iters.update({
                    'card_number': self.credit_card_data.get('card_number'),
                    'card_cvv': self.credit_card_data.get('card_cvv'),
                    'card_expiration_date':
                        self.credit_card_data.get('card_expiration_date'),
                    'card_holder_name':
                        self.credit_card_data.get('card_holder_name'),
                })

        # now 'yield' through the items
        for x, y in iters.items():
            yield x, y

    def _set_default_metadata_items(self):
        # Estabelecer uma referência de qual o estado sistema houve a transação
        environment_version = os.getenv('ENVIRONMENT_VERSION')
        if environment_version:
            self.add_metadata('versão do sistema', environment_version)

    def _check_errors(self):
        self.errors = dict()

        if self.payment_method not in [self.BOLETO, self.CREDIT_CARD]:
            self.errors['payment_method'] = \
                'Tipo de pagamento inválido. Você deve informar' \
                ' "boleto ou credit_card".' \
                ' Valor informado: {}'.format(self.payment_method)

        if self.payment_method == self.CREDIT_CARD:
            if not self.credit_card_hash and not self.credit_card_data:
                self.errors['payment_method'] = \
                    'Dados de cartão inválidos: informe card_hash ou dados' \
                    ' do cartão de crédito.'

        if not self.amount:
            self.errors['amount'] = 'Você deve informar um valor.'

        receivers_amount = Decimal(0)

        for rule in self.split_rules:
            receivers_amount += rule.amount

        # Aceite de diferença de até 1 centavo
        assert round(receivers_amount, 2) == round(self.amount, 2), \
            '{} != {}'.format(
                round(receivers_amount, 2),
                round(self.amount, 2),
            )

        invalid_items = dict()
        for item in self.items:
            if item.is_valid() is False:
                invalid_items[item.identifier] = item.errors

        if len(invalid_items):
            msg = "Alguns itens são inválidos:"
            for title, errors in invalid_items.items():
                msg += ' {}: {}'.format(title, ', '.join(errors))

            self.errors['items'] = msg
