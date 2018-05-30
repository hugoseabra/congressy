"""
Recebedores de rateamento de itens vendidos na platforma.
"""

from decimal import Decimal

from partner import constants as partner_constants
from . import constants


class Receiver(object):
    """
    Definição absoluta de Recebedor de um rateamento (split) de itens
    comercializados.
    """
    level = None

    def __init__(self,
                 type,
                 id: str,
                 amount: Decimal,
                 chargeback_responsible=False,
                 processing_fee_responsible=False) -> None:
        self.type = type
        self.id = id
        self.amount = amount
        self.chargeback_responsible = chargeback_responsible
        self.processing_fee_responsible = processing_fee_responsible

    @property
    def amount(self) -> Decimal:
        return self.__amount

    @amount.setter
    def amount(self, amount: Decimal) -> None:
        self.__amount = amount

    @property
    def chargeback_responsible(self) -> bool:
        return self.__chargeback_responsible

    @chargeback_responsible.setter
    def chargeback_responsible(self, is_responsible: bool) -> None:
        self.__chargeback_responsible = is_responsible

    @property
    def processing_fee_responsible(self) -> bool:
        return self.__processing_fee_responsible

    @processing_fee_responsible.setter
    def processing_fee_responsible(self, is_responsible: bool) -> None:
        self.__processing_fee_responsible = is_responsible

    def __iter__(self):
        iters = {
            'id': self.id,
            'amount': self.amount,
            'chargeback_responsible': self.chargeback_responsible,
            'processing_fee_responsible': self.processing_fee_responsible,
        }

        # now 'yield' through the items
        for x, y in iters.items():
            yield x, y


class CongressyReceiver(Receiver):
    """
    Definição Congressy como Recebedora de um rateamento (split) de itens
    comercializado.
    """
    level = constants.RECEIVER_LEVEL0

    def create_and_publish_partners(self,
                                    receiver_subscriber,
                                    subscription) -> None:
        """
        Cria e publica recebedores parceiros que irã participar do rateamente
        de inscrição.
        """
        event = subscription.event

        # Verifica se há parceiros
        partners = subscription.event.partner_contracts.filter(
            partner__status=partner_constants.ACTIVE,
            partner__approved=True
        )

        partners_total_amount = 0
        partner_rules = []
        for contract in partners:

            try:
                id = contract.partner.bank_account.recipient_id
            except AttributeError:
                id = None

            if not id:
                raise Exception(
                    'O parceiro "{} (ID: {})" não possui'
                    ' "recipient_id".'.format(
                        constract.partner.person.name,
                        constract.partner.pk,
                    )
                )

            percent_decimal = Decimal(contract.partner_plan.percent) / 100

            # O parceiro ganha em cima do valor liquido da Congressy.
            partner_amount = self.amount * percent_decimal
            partners_total_amount += partner_amount

            partner_receiver = ComissioningReceiver(
                type=self.type,
                id=id,
                amount=partner_amount,
                chargeback_responsible=True,
                processing_fee_responsible=False,
                parent_receiver=self,
            )
            receiver_subscriber.publish(partner_receiver)

        self.amount = partners_total_amount


class OrganizerReceiver(Receiver):
    level = constants.RECEIVER_LEVEL0

    def __init__(self,
                 installment_result,
                 transfer_taxes=False,
                 *args,
                 **kwargs):

        self.transfer_taxes = transfer_taxes
        self.installment_result = installment_result

        super().__init__(*args, **kwargs)

    def __iter__(self):
        parent_iters = super().__iter__()
        iters = {}
        for x, y in parent_iters:
            iters[x] = y

        iters.update({
            'transfer_taxes': self.transfer_taxes is True,
            'installment_result': dict(self.installment_result),
        })

        for x, y in iters.items():
            yield x, y


class ComissioningReceiver(Receiver):
    level = constants.RECEIVER_LEVEL1

    def __init__(self, parent_receiver, name, *args, **kwargs):

        self.parent_receiver = parent_receiver

        super().__init__(*args, **kwargs)

        self.parent_receiver.percent -= self.percent
        self.parent_receiver.amount -= self.amount

    def __iter__(self):
        parent_iters = super().__iter__()
        iters = {}
        for x, y in parent_iters:
            iters[x] = y

        iters.update({
            'parent_receiver': dict(self.parent_receiver),
            'name': dict(self.name),
        })

        for x, y in iters.items():
            yield x, y
