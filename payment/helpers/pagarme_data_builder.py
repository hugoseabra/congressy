import os
import uuid
from datetime import timedelta, datetime
from decimal import Decimal

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
from payment.helpers.postback_url import get_postback_url
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
        self.debts = list()
        self.debt_items = dict()
        self.liquid_amount = Decimal(0)
        self.has_expiration_date = False

        event = subscription.event

        lot = subscription.lot
        self.metadata_items = {
            'organização': event.organization.name,
            'evento': event.name,
            'lote': '{} ({})'.format(lot.display_publicly, lot.pk),
            'código': subscription.code,
        }

        # Estabelecer uma referência de qual o estado sistema houve a transação
        environment_version = os.getenv('ENVIRONMENT_VERSION')
        if environment_version:
            self.metadata_items['system'] = {
                'version': environment_version,
                'environment': 'production'
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

    def build(self, amount, transaction_type, installments=1, card_hash=None):

        lot = self.subscription.lot
        event = self.subscription.event

        self._check_transaction_type(transaction_type, card_hash)
        self._check_debts(amount, installments)

        transaction_id = str(uuid.uuid4())

        soft_desc = lot.event.organization.name[:13].strip()

        split_rules = self._create_split_rules(amount,
                                               transaction_type,
                                               installments)

        data = {
            'api_key': settings.PAGARME_API_KEY,
            'transaction_id': transaction_id,
            'postback_url': get_postback_url(transaction_id),
            # 13 caracteres
            'soft_descriptor': soft_desc,
            'amount': self.as_payment_format(amount),
            'liquid_amount': self.as_payment_format(self.liquid_amount),
            'price': self.as_payment_format(amount),
            'payment_method': transaction_type,
            "installments": installments,
            "metadata": self.metadata_items,
            "items": [item for _, item in self.debt_items.items()],
            "split_rules": split_rules,
        }

        if transaction_type == Transaction.BOLETO:
            # TOTAL: 255 caracteres

            # Instrução 1: 99 caracteres
            instructions = 'IMPORTANTE:  Após o vencimento não há garantia ' \
                           'do mesmo valor e sua reserva de vaga poderá ' \
                           'expirar.'

            # Instrução 2: 47 caracteres
            instructions += 'Ev.: {}. Lote: {}. Insc.: {}.'.format(
                self.subscription.event.name[:8],
                self.subscription.lot.name[:8],
                self.subscription.code,  # 8 caracteres
            )

            data['boleto_instructions'] = instructions

            assert len(instructions) <= 255, 'boleto_instructions len({})' \
                                             ''.format(len(instructions))

            event_config = event.feature_configuration

            if event_config.feature_boleto_expiration_on_lot_expiration:
                # Pagarme sets to one day before, so we set one day forward
                # to 2 days after lot ends.
                next_day = lot.date_end + timedelta(days=1)
                exp_date = next_day.strftime('%Y-%m-%d')

                data['boleto_expiration_date'] = exp_date

            else:
                # Deve-se verificar se o evento começou.
                #   Se sim: não podemos gerar boletos.
                #   Se não, há quantos dias estamos antes do evento:
                #     Se 1 dia antes do evento: o boleto deve ter a data de
                #       vencimento de hoje.
                #     Se 2 dias, o boleto deve ter a data de vencimento 1 dia
                #       antes do evento.
                #   Se mais de 2 dias, processamento padrão: vencimento padrão
                #     de 2 dia do pagarme.

                if event.running is True:
                    raise TransactionDataError(
                        'Evento já iniciou e não pode gerar novas transações'
                        ' de boleto.'
                    )

                now = datetime.now()
                diff_days = event.date_start - now

                expiration_date = None

                if diff_days.days == 1:
                    expiration_date = now - timedelta(days=1)

                elif diff_days.days == 2:
                    expiration_date = now

                if expiration_date:
                    data['boleto_expiration_date'] = \
                        expiration_date.strftime('%Y-%m-%d')

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
                        'type': person.international_doc_type,
                        'number': person.international_doc,
                    }
                ],
                'phone_numbers': [
                    self.clear_string(person.get_phone_display())
                ],
            })

        billing_address = dict()

        if is_brazil is True:
            billing_address.update({
                "country": "br",
                "neighborhood": person.village or '',
                "street": person.street or '',
                "street_number": person.number or 'S/N',
                "city": person.city.name.lower().capitalize(),
                "state": person.city.uf.lower(),
                "zipcode": person.zip_code,
            })

        else:
            billing_address.update({
                "street": person.address_international,
                "country": person.country.lower(),
                "city": person.city_international,
                "state": person.state_international,
                "zipcode": person.zip_code_international or '000',
            })

        data['billing'] = {
            "name": person.name,
            "address": billing_address,
        }

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
            boleto_allowed = is_boleto_allowed(
                self.subscription.event
            ) is True and open_boleto_queryset.count() == 0

            if boleto_allowed is False:
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

    def _create_split_rules(self, amount, transaction_type, installments=1):
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
            transaction_type=transaction_type,
            subscription=self.subscription,
            amount=amount,
            installments=installments,
        )

        # Por enquanto, receivers somente de inscrições
        publisher.create_and_publish_subscription()

        total_receivers_amount = Decimal(0)
        for _, receiver in subscriber.receivers.items():
            total_receivers_amount += round(receiver.amount, 2)

        # Verifica se a soma do rateamento é diferente do split. Se sim,
        # vamos pegar o resto e atribuir para a Congressy;
        diff = \
            total_receivers_amount - round(amount, 2)

        split_rules = []
        for _, receiver in subscriber.receivers.items():
            r_amount = receiver.amount

            if receiver.org_receiver is True:
                self.liquid_amount = receiver.liquid_amount

            if diff != 0 and receiver.congressy_receiver is True:
                r_amount -= diff

            split_rules.append({
                "recipient_id": receiver.id,
                "amount": self.as_payment_format(r_amount),
                "liable": receiver.chargeback_responsible,
                "charge_processing_fee": receiver.processing_fee_responsible
            })

        return split_rules

    @staticmethod
    def clear_string(string):
        if not string:
            return ''

        return string \
            .replace('.', '') \
            .replace('-', '') \
            .replace('/', '') \
            .replace('(', '') \
            .replace(')', '') \
            .replace(' ', '')
