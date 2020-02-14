from abc import ABCMeta, abstractmethod
from datetime import timedelta, date
from decimal import Decimal

import absoluteuri

from gatheros_event.models import Event
from gatheros_subscription.models import Subscription, Lot
from payment.helpers.postback_url import get_postback_url
from payment.pagarme.transaction.billing import Billing
from payment.pagarme.transaction.customer import Customer
from payment.pagarme.transaction.item import Item
from payment.pagarme.transaction.receiver_creator import \
    TransactionReceiverCreator
from payment.pagarme.transaction.split_rule import SplitRule
from payment.pagarme.transaction.transaction import PagarmeTransaction


class AbstractPagarmeTransactionBuilder:
    __metaclass__ = ABCMeta

    def __init__(self,
                 event: Event,
                 lot: Lot,
                 pagarme_transaction: PagarmeTransaction,
                 installment_part=None):

        self.pagarme_transaction = pagarme_transaction

        self.event = event
        self.lot = lot
        self.category = self.lot.category if self.lot.category_id else None
        self.organization = event.organization

        if installment_part is not None:
            # Instância de Part ou GroupPart
            self.installment_part = installment_part

            # instância de installment.Contract ou installment.GroupContract
            self.contract = installment_part.contract

        else:
            self.installment_part = None
            self.contract = None

        self.pagarme_transaction.add_metadata(
            'congressy_percent',
            '{}%'.format(self.event.congressy_percent)
        )
        self.pagarme_transaction.add_metadata(
            'transfer_tax',
            1 if self.lot.transfer_tax is True else 0
        )

        # organização
        self.pagarme_transaction.add_metadata('organization_id',
                                              self.organization.pk)

        self.pagarme_transaction.add_metadata('organization',
                                              self.organization.name)

        self.pagarme_transaction.add_metadata('event_id', self.event.pk)
        self.pagarme_transaction.add_metadata('event', self.event.name)
        self.pagarme_transaction.add_metadata('link', absoluteuri.reverse(
            'public:hotsite',
            kwargs={'slug': self.event.slug}
        ))

        # Uma vez processado, o builder não será mais reprocessado para não
        # haver discrepância entre seu estado computado e o estado de
        # self.pagarme_transaction.
        self._processed = False

    def set_as_credit_card_hash(self, card_hash: str):
        self.pagarme_transaction.set_as_credit_card_hash(card_hash)

    def set_as_credit_card_data(self,
                                card_number: str,
                                card_cvv: str,
                                card_expiration_date: str,
                                card_holder_name: str):
        self.pagarme_transaction.set_as_credit_card_data(
            card_number=card_number,
            card_cvv=card_cvv,
            card_expiration_date=card_expiration_date,
            card_holder_name=card_holder_name
        )

    def set_as_boleto(self, expiration_date: date = None):

        if expiration_date is None:
            expiration_date = self._get_expiration_date()

        self.pagarme_transaction.set_boleto_data(
            boleto_instructions=self._get_boleto_instructions(),
            soft_descriptor=self._get_soft_descriptor(),
            expiration_date=expiration_date,
        )

    def set_postback_url(self, url):
        if self._processed is True:
            raise Exception(
                'Não é possível inserir url de postack a um builder que já foi'
                ' processado.'
            )

        self.pagarme_transaction.set_postaback_url(url)

    def set_customer(self,
                     external_id: str,
                     name: str,
                     email: str,
                     doc_type: str,
                     doc_number: str,
                     phones: list = None,
                     country: str = None):
        if self._processed is True:
            raise Exception(
                'Não é possível dados de customer ao builder que já foi'
                ' processado.'
            )

        self.pagarme_transaction.set_customer(Customer(
            external_id,
            name,
            email,
            doc_type,
            doc_number,
            phones,
            country
        ))

        self.pagarme_transaction.add_metadata('pagador', external_id)

    def set_billing(self,
                    name: str,
                    street: str,
                    zipcode: str,
                    city: str,
                    state: str,
                    street_number: str = None,
                    neighborhood: str = None,
                    complement: str = None,
                    country: str = None):
        if self._processed is True:
            raise Exception(
                'Não é possível dados de billing ao builder que já foi'
                ' processado.'
            )

        self.pagarme_transaction.set_billing(Billing(
            name,
            street,
            zipcode,
            city,
            state,
            street_number,
            neighborhood,
            complement,
            country,
        ))

    def add_item(self,
                 identifier: str,
                 title: str,
                 amount: Decimal,
                 liquid_amount: Decimal,
                 quantity: int):
        if self._processed is True:
            raise Exception(
                'Não é possível adicionar itens ao builder que já foi'
                ' processado.'
            )

        item = Item(
            identifier=identifier,
            title=self._get_debt_title(title),
            unit_price=amount,
            liquid_unit_price=liquid_amount,
            quantity=quantity,
            tangible=False,
        )

        self.pagarme_transaction.add_item(item)

    def build(self):
        if self._processed is False:
            self._create_split_rules()

            if self.pagarme_transaction.is_valid() is False:
                raise Exception(self.pagarme_transaction.errors)

        self._processed = True

        return dict(self.pagarme_transaction)

    @abstractmethod
    def _get_boleto_instructions(self):
        pass

    @abstractmethod
    def _get_expiration_date(self):
        pass

    def _get_soft_descriptor(self):
        return self.event.organization.name[:13]

    def _get_debt_title(self, title: str):
        if self.contract and self.installment_part:
            title += ' - {} ({}/{})'.format(
                self.contract.pk,
                self.installment_part.installment_number,
                self.contract.num_installments,
            )

        return title

    def _create_split_rules(self):
        """
        Constroi as regras de split da transação.
        """
        if self._processed is True:
            return

        if not self.pagarme_transaction.amount:
            raise Exception('Não é possível criar split de recebedores sem'
                            ' um montante para divisão.')

        receiver_creator = TransactionReceiverCreator(
            transaction_type=self.pagarme_transaction.payment_method,
            event=self.event,
            lot=self.lot,
            amount=self.pagarme_transaction.amount,
            installments=self.pagarme_transaction.installments,
            interests_amount=self.pagarme_transaction.interests_amount,
        )

        total_receivers_amount = Decimal(0)
        for receiver in receiver_creator.get_receivers():
            total_receivers_amount += round(receiver.amount, 2)

        # Verifica se a soma do rateamento é diferente do split. Se sim,
        # vamos pegar o resto e atribuir para a Congressy;
        diff = \
            total_receivers_amount - round(self.pagarme_transaction.amount, 2)

        for receiver in receiver_creator.get_receivers():
            r_amount = receiver.amount

            if receiver.org_receiver is True:
                self.liquid_amount = receiver.liquid_amount

            if diff != 0 and receiver.congressy_receiver is True:
                r_amount -= diff

            self.pagarme_transaction.add_split_rule(SplitRule(
                recipient_id=receiver.identifier,
                amount=round(r_amount, 2),
                liable=receiver.chargeback_responsible,
                charge_processing_fee=receiver.processing_fee_responsible,
            ))


class SubscriptionTransactionBuilder(AbstractPagarmeTransactionBuilder):
    def __init__(self, subscription: Subscription, *args, **kwargs):
        self.subscription = subscription

        self.person = subscription.person

        kwargs['event'] = subscription.event
        kwargs['lot'] = subscription.lot

        super().__init__(*args, **kwargs)

        self.set_postback_url(
            url=get_postback_url(self.pagarme_transaction.transaction_id)
        )

        self._set_metadata_items()
        self._add_items()

    def _set_metadata_items(self):
        # participante
        self.pagarme_transaction.add_metadata('person_name',
                                              self.person.name)
        self.pagarme_transaction.add_metadata('person_email',
                                              self.person.email)
        self.pagarme_transaction.add_metadata('person_id',
                                              str(self.person.pk))
        self.pagarme_transaction.add_metadata(
            'person_phone',
            str(self.person.get_phone_display()),
        )

        # sobre inscrição
        if self.category:
            self.pagarme_transaction.add_metadata(
                'lot_category',
                self.category.name
            )
            self.pagarme_transaction.add_metadata(
                'lot_category_id',
                self.category.pk
            )

        self.pagarme_transaction.add_metadata('lot_id', self.lot.pk)

        self.pagarme_transaction.add_metadata('subscription_id',
                                              str(self.subscription.pk))

        limit = self.event.limit
        num_subscription = self.subscription.event_count
        if limit > 0:
            vacancy = '{}/{}'.format(num_subscription, limit)
        else:
            vacancy = num_subscription

        self.pagarme_transaction.add_metadata('vacancy', vacancy)

        if self.installment_part:
            contract = self.installment_part.contract
            self.pagarme_transaction.add_metadata('installment_contract',
                                                  contract.pk)
            self.pagarme_transaction.add_metadata(
                'installment_part',
                '{}/{}'.format(
                    self.installment_part.installment_number,
                    contract.num_installments
                )
            )

        # if self.subscription.category_coupon_id:
        #
        #     coupon = self.subscription.category_coupon
        #     coupon_value = 'Cupom de categoria: {}'.format(coupon.name)
        #
        #     if coupon.value:
        #         if coupon.discount_type == coupon.VALUE:
        #             coupon_value += ' (R$ {})'.format(localize(coupon.value))
        #         elif coupon.discount_type == coupon.PERCENT:
        #             coupon_value += ' ({}%)'.format(coupon.value)
        #
        #     self.pagarme_transaction.add_metadata('Cupom de categoria',
        #                                           coupon_value)
        #     self.pagarme_transaction.add_metadata('ID Cupom de categoria',
        #                                           coupon.pk)

    def _get_boleto_instructions(self):
        """ Não pode ultrapassar mais de 255 caracteres """

        # Instrução 1: 86 caracteres
        instructions1 = 'Após o vencimento não há garantia de vaga disponível' \
                        ' e o preço pode sofrer alterações.'

        # Instrução 2: 83 caracteres
        instructions2 = ' 1 dia após o vencimento do boleto, sua vaga será' \
                        ' liberada para outro participante.'

        # Instrução 3: 30 + 10 + 4 (possivel) + 8 (id da categoria) = 52
        instructions3 = ' Ev.: {}. Lote: {}. Insc.: {}.'.format(
            self.event.name[:10],
            self.subscription.lot.name[:10],
            self.subscription.code,  # 8 caracteres
        )

        num_chars = len(instructions1) \
                    + len(instructions2) \
                    + len(instructions3)

        if num_chars > 255:
            # Só vai acontecer se
            diff = num_chars - 255
            # Diminuir a instrução 2
            instructions2 = instructions2[0:len(instructions2) - diff]

        instructions = instructions1 + instructions2 + instructions3

        assert len(instructions) <= 255, 'boleto_instructions len({})' \
                                         ''.format(len(instructions))

        return instructions

    def _get_expiration_date(self):
        event_config = self.event.feature_configuration

        if not event_config.feature_boleto_expiration_on_lot_expiration:
            return None

        # Pagarme sets to one day before, so we set one day forward.
        next_day = self.lot.date_end + timedelta(days=1)
        return next_day.date()

    def _add_items(self):
        # ---------------------------------------------------------------------
        # SE É UMA TRANSAÇÃO DE PARCELA:
        # - O total a transacionar será o valor da parcela.
        #
        # CASO CONTRÁRIO
        # - O total a transacionar é será o valor pendente da inscrição
        # ---------------------------------------------------------------------

        debts_amount = self.subscription.debts_amount

        if self.installment_part is not None:
            total_amount = self.installment_part.amount

            perc = (total_amount * 100) / debts_amount

            self.pagarme_transaction.add_metadata(
                'valor pago proporcional',
                '{}%'.format(round(perc, 2))
            )
        else:
            total_amount = debts_amount

        if not total_amount:
            raise Exception('Não há valor a transacionar no builder.')

        for debt in self.subscription.debts_list:
            if self.installment_part is not None:
                # Pagamento é parcial ao montante total a pagar.
                perc = ((debt.amount * 100) / total_amount) / 100

                assert perc <= 100, \
                    'Percentual maior do que o pagamento:' \
                    ' {} > 100'.format(round(perc, 2))

                amount = debt.total_amount * perc
                liquid_amount = debt.liquid_amount * perc
            else:
                amount = debt.total_amount
                liquid_amount = debt.liquid_amount

            self.add_item(
                identifier=debt.item_id,
                title=debt.name,
                amount=amount,
                liquid_amount=liquid_amount,
                quantity=1,  # @TODO - dar suporte a quantidade em Debt.
            )
