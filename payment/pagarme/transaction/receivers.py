"""
Recebedores de rateamento de itens vendidos na platforma.
"""

from decimal import Decimal

from django.conf import settings

from partner import constants as partner_constants

RECEIVER_LEVEL0 = 'level0'
RECEIVER_LEVEL1 = 'level1'


class Receiver(object):
    """
    Definição absoluta de Recebedor de um rateamento (split) de itens
    comercializados.
    """
    level = None
    congressy_receiver = False
    org_receiver = False

    def __init__(self,
                 receiver_type: str,
                 identifier: str,
                 amount: Decimal,
                 chargeback_responsible=False,
                 processing_fee_responsible=False) -> None:
        self.receiver_type = receiver_type
        self.identifier = identifier
        self.amount = amount
        self.chargeback_responsible = chargeback_responsible
        self.processing_fee_responsible = processing_fee_responsible

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
            'id': self.identifier,
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
    level = RECEIVER_LEVEL0
    congressy_receiver = True

    def create_and_publish_partners(self, event) -> list:
        """
        Cria e publica recebedores parceiros que irã participar do rateamente
        de inscrição.
        """
        # Verifica se há parceiros
        partners = event.partner_contracts.filter(
            partner__status=partner_constants.ACTIVE,
            partner__approved=True
        )

        cgsy_total_amount = self.amount
        partner_receivers = []
        for contract in partners:
            try:
                identifier = contract.partner.bank_account.recipient_id
            except AttributeError:
                raise Exception(
                    'O parceiro "{} (ID: {})" não possui'
                    ' "recipient_id".'.format(
                        contract.partner.person.name,
                        contract.partner.pk,
                    )
                )

            percent_decimal = Decimal(contract.partner_plan.percent) / 100

            # O parceiro ganha em cima do valor liquido da Congressy.
            partner_amount = self.amount * percent_decimal
            cgsy_total_amount -= partner_amount

            partner_receiver = ComissioningReceiver(
                name='partner',
                receiver_type=self.receiver_type,
                identifier=identifier,
                amount=round(partner_amount, 2),
                chargeback_responsible=True,
                processing_fee_responsible=False,
                parent_receiver=self,
            )
            partner_receivers.append(partner_receiver)

        self.amount = round(cgsy_total_amount, 2)

        return partner_receivers


class OrganizerReceiver(Receiver):
    level = RECEIVER_LEVEL0

    def __init__(self,
                 installment_result,
                 transfer_taxes=False,
                 *args,
                 **kwargs):

        self.transfer_taxes = transfer_taxes
        self.installment_result = installment_result

        kwargs.update({
            'processing_fee_responsible': False,
        })

        if settings.DEBUG is True and \
                hasattr(settings, 'PAGARME_TEST_RECIPIENT_ID'):
            kwargs.update({
                'identifier': settings.PAGARME_TEST_RECIPIENT_ID,
            })

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
    level = RECEIVER_LEVEL1

    def __init__(self, parent_receiver, name, *args, **kwargs):

        self.parent_receiver = parent_receiver
        self.name = name

        super().__init__(*args, **kwargs)

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
