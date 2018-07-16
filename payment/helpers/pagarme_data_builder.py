import os
import uuid
from datetime import timedelta
from decimal import Decimal

import absoluteuri
from django.conf import settings

from payment.exception import (
    TransactionDataError,
)
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

    def __init__(self, subscription):

        self.subscription = subscription
        self.debts = []
        self.debt_items = {}
        self.debt_amount = Decimal(0)
        self.liquid_amount = Decimal(0)
        self.has_expiration_date = False

        lot = subscription.lot
        self.metadata_items = {
            'lote': '{} ({})'.format(lot.display_publicly, lot.pk),
            'código': subscription.code,
        }

        # Estabelecer uma referência de qual o estado sistema houve a transação
        environment_version = os.getenv('ENVIRONMENT_VERSION')
        if environment_version:
            self.metadata_items['system'] = {
                'version': environment_version,
                'enviroment': 'production'
            }

    def add_debt(self, debt):
        if debt.id in self.debt_items:
            return

        if not debt.amount:
            return

        if debt.subscription != self.subscription:
            raise TransactionDataError(
                'A pendência financeira "{}" não pertence à inscrição'
                ' "{}"'.format(debt, self.subscription)
            )

        self.debts.append(debt)
        self.debt_items[debt.id] = {
            "id": debt.item_id,
            "title": debt.name,
            "unit_price": self.as_payment_format(debt.amount),
            "quantity": 1,
            "tangible": False
        }
        self.debt_amount += debt.amount
        self.liquid_amount += debt.liquid_amount

    def build(self, amount, transaction_type, installments=1, card_hash=None):

        lot = self.subscription.lot

        self._check_transaction_type(transaction_type, card_hash)
        self._check_debts(amount, installments)

        transaction_id = str(uuid.uuid4())

        postback_url = absoluteuri.reverse(
            'api:payment:payment_postback_url',
            kwargs={'uidb64': transaction_id}
        )

        data = {
            'api_key': settings.PAGARME_API_KEY,
            'transaction_id': transaction_id,
            'postback_url': postback_url,
            # 13 caracteres
            'soft_descriptor': lot.event.organization.name[:13],
            'amount': self.as_payment_format(amount),
            'liquid_amount': self.as_payment_format(self.liquid_amount),
            'price': self.as_payment_format(amount),
            'payment_method': transaction_type,
            "installments": installments,
            "metadata": self.metadata_items,
            "items": [item for id, item in self.debt_items.items()],
            "split_rules": self._create_split_rules(amount, installments),
        }

        if transaction_type == Transaction.BOLETO:
            # TOTAL: 255 caracteres
            # Instrução 1: 111 caracteres
            instructions = 'Após o vencimento não há garantia de que o' \
                            ' Lote estará disponível. Isso pode mudar o' \
                            ' preço de sua inscrição.'

            # Instrução 2: 97 caracteres
            instructions += ' IMPORTANTE: após 3 dias de vencimento do' \
                            ' boleto, sua vaga será liberada para outro' \
                            ' participante.'

            # Instrução 3: 47 caracteres
            instructions += 'Ev.: {}. Lote: {}. Insc.: {}.'.format(
                self.subscription.event.name[:8],
                self.subscription.lot.name[:8],
                self.subscription.code, # 8 caracteres
            )

            data['boleto_instructions'] = instructions

            if subscription.event.allow_boleto_expiration_on_lot_expiration:
                # Pagarme sets to one day before, so we set one day forward.
                next_day = lot.date_end + timedelta(days=1)
                exp_date = next_day.strftime('%Y-%m-%d')

                data['boleto_expiration_date'] = exp_date

        if transaction_type == Transaction.CREDIT_CARD:
            data['card_hash'] = card_hash

        person = self.subscription.person
        is_brazil = person.country == 'BR'

        data['customer'] = {
            'external_id': str(self.subscription.pk),
            'name': person.name,
            'type': 'individual',
            'email': person.email,
        }

        if person.birth_date:
            data['customer'].update({
                'birthday': person.birth_date.strftime('%Y-%m-%d')
            })

        if is_brazil is True:
            data['customer'].update({
                'country': 'br',
                'documents': [
                    {
                        'type': 'cpf',
                        'number': self.clear_string(person.cpf),
                    }
                ],
                'phone_numbers': [
                    self.clear_string(person.get_phone_display())
                ],
            })

        else:
            data['customer'].update({
                'country': person.country.lower(),
                'documents': [
                    {
                        'type': 'ID/PASSPORT',
                        'number': person.international_doc,
                    }
                ],
                'phone_numbers': [
                    self.clear_string(person.get_phone_display())
                ],
            })

        data['billing'] = {
            "name": person.name,
            "address": {
                "neighborhood": person.village or '',
                "street": person.street or '',
                "street_number": person.number or 'S/N',
            }
        }

        if is_brazil is True:
            data['billing']['address'].update({
                "country": "br",
                "city": person.city.name.lower().capitalize(),
                "state": person.city.uf.lower(),
                "zipcode": person.zip_code,
            })

        else:
            data['billing']['address'].update({
                "country": person.country.lower(),
                "city": person.city_international.lower().capitalize(),
                "state": person.state_international.lower().capitalize(),
                "zipcode": person.zip_code_international,
            })

        return data

    @staticmethod
    def as_decimal(value):
        # Contexto de construção de números decimais
        return amount_as_decimal(value)

    @staticmethod
    def as_payment_format(value):
        return decimal_processable_amount(value)

    def _check_transaction_type(self, transaction_type, card_hash=None):
        if not transaction_type:
            raise TransactionDataError('Nenhum tipo de transação informado.')

        if transaction_type == Transaction.BOLETO:
            open_boleto_queryset = \
                get_opened_boleto_transactions(self.subscription)

            # se o evento permite boleto e se a inscrição não possui boletos
            # em aberto (não-vencidos)
            bolleto_allowed = is_boleto_allowed(
                self.subscription.event
            ) is True and open_boleto_queryset.count() == 0

            if bolleto_allowed is False:
                raise TransactionDataError(
                    'Pagamento com boleto não permitido.'
                )

        is_credit_card = transaction_type == Transaction.CREDIT_CARD
        if is_credit_card and not card_hash:
            raise TransactionDataError('O hash do cartão não foi encontrado.')

    def _check_debts(self, amount, installments):
        assert isinstance(amount, Decimal)

        for debt in self.debts:
            if debt.installments != installments:
                raise TransactionDataError(
                    'A pendência "{}" possui parcelamento em "{}x", mas a'
                    ' os dados de transação a serem criados é de'
                    ' "{}x".'.format(
                        debt,
                        debt.installments,
                        installments
                    )
                )

        if self.debt_amount > amount:
            raise TransactionDataError(
                'Valor de transações de pendências inseridas ultrapassa'
                ' o montante principal a ser transacionado.'
            )

    def _create_split_rules(self, amount, installments=1):
        """
        Contsroi as regras de split da transação.
        :param amount:
            Valor padronizado conforme exigido pelo Pagar.me, ou seja, os
            centavos são junto com o valor principal, sem separação de vingula.
        :return:
        """

        subscriber = ReceiverSubscriber(amount=amount)
        publisher = ReceiverPublisher(
            receiver_subscriber=subscriber,
            subscription=self.subscription,
            amount=amount,
            installments=installments,
        )

        # Por enquanto, receivers somente de inscrições
        publisher.create_and_publish_subscription()

        split_rules = []
        for id, receiver in subscriber.receivers.items():
            split_rules.append({
                "recipient_id": id,
                "amount": self.as_payment_format(receiver.amount),
                "liable": receiver.chargeback_responsible,
                "charge_processing_fee": receiver.processing_fee_responsible
            })

        return split_rules

    @staticmethod
    def clear_string(string):
        return string \
            .replace('.', '') \
            .replace('-', '') \
            .replace('/', '') \
            .replace('(', '') \
            .replace(')', '') \
            .replace(' ', '')
