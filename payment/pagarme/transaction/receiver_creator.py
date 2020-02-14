"""
Gerenciamento de coleções de Receivers que serão usados para diferentes
operações de processamento para obter regras de rateamento de pagamento.
"""
from datetime import date
from decimal import Decimal

from django.conf import settings

from gatheros_event.models import Event
from gatheros_subscription.models import Lot
from payment.installments import Calculator, InstallmentResult
from payment.pagarme.transaction.receivers import (
    CongressyReceiver,
    OrganizerReceiver,
)
from payment.payable.credit_card import get_payables

RECEIVER_TYPE_SUBSCRIPTION = 'receiver_subscription'
RECEIVER_TYPE_PRODUCT = 'receiver_product'
RECEIVER_TYPE_SERVICE = 'receiver_service'


class TransactionReceiverCreator(object):
    """
    Publicador de Recebedores de acordo com inscrição informada.
    """

    def __init__(self,
                 transaction_type: str,
                 event: Event,
                 lot: Lot,
                 amount: Decimal,
                 installments: int,
                 interests_amount=Decimal(0)) -> None:

        self.transaction_type = transaction_type

        self.event = event
        self.lot = lot
        self.organization = event.organization

        self.amount = amount
        self.interests_amount = interests_amount

        self.installments = installments

        self.interests_rate = Decimal(
            float(settings.CONGRESSY_INSTALLMENT_INTERESTS_RATE) / 100
        )

        self.cgsy_percent = Decimal(float(self.event.congressy_percent) / 100)

        self.installment_calculator = Calculator(
            interests_rate=self.interests_rate,
            total_installments=10,
            free_installments=int(self.lot.num_install_interest_absortion),
        )

        self._check_criterias()

    def is_cc(self) -> bool:
        return self.transaction_type == 'credit_card'

    def is_boleto(self) -> bool:
        return self.transaction_type == 'boleto'

    def get_original_amount(self):
        """
        Regata o montante configurado como preço original levando em
        consideração a retirada de juros e taxa de transferência (se houver).
        """

        total_proportional = Decimal(100)

        if self.lot.transfer_tax is True:
            total_proportional = Decimal(100 + (self.cgsy_percent * 100))

        total_percent = round(total_proportional / 100, 1)

        # Valor sem juros embutidos.
        amount_no_interests = self.amount - self.interests_amount

        # A divisão pelo percentual se dá pelo cálculo reverso de percentual.
        return amount_no_interests / total_percent

    def get_payables_amount(self, payable_amount: Decimal,
                            fee_percent: Decimal = None):
        """
        Resgata valor de recebíveis
        """
        # Agora vamos verificar possíveis valores de taxa de
        # antecipação paga pelo participante no parcelamento
        amount = Decimal(0)

        if self.is_cc() is True and self.installments > 1:
            payables = get_payables(
                recipient_id=self.organization.recipient_id,
                transaction_amount=self.amount,
                transaction_date=date.today(),
                payable_amount=payable_amount,
                installments=self.installments,
                fee_percent=fee_percent,
                antecipation_fee_percent=Decimal(1.99),
            )

            for payable in payables:
                amount += payable.get_antecipation_amount()

        return amount

    def get_congressy_amount(self):
        original_amount = self.get_original_amount()
        cgsy_amount = original_amount * self.cgsy_percent

        minimum_amount = Decimal(
            getattr(settings, 'CONGRESSY_MINIMUM_AMOUNT', 0)
        )

        # Mínimo aplicável apenas para inscrição.
        if minimum_amount and cgsy_amount < minimum_amount:
            cgsy_amount = minimum_amount

        cgsy_amount += self.interests_amount

        # Se o organizador assumiu juros de parcelamento, o montante a ser
        # transacionado estará sem o valor de juros de parcelamento. Então,
        # vamos recalcula-los e repassar os juros para a Congressy.

        if 1 < self.installments <= self.lot.num_install_interest_absortion:
            if not self.interests_amount:
                free_interests_amount = \
                    self.installment_calculator.get_absorbed_interests_amount(
                        amount=self.amount,
                        installments=self.installments,
                    )

                cgsy_amount += free_interests_amount

        return cgsy_amount

    def get_organizer_amount(self):
        cgsy_amount = self.get_congressy_amount()
        return self.amount - cgsy_amount

    def get_receivers(self):
        """
        Cria e publica recebedores que irã participar do rateamente de uma
        inscrição.
        """
        cgsy_amount = round(self.get_congressy_amount(), 2)
        org_amount = round(self.get_organizer_amount(), 2)

        org_payable_amount = \
            self.get_payables_amount(payable_amount=org_amount)

        cgsy_amount -= org_payable_amount
        org_amount += org_payable_amount

        # ==== RECEIVERS
        receivers = list()

        cgsy_receiver = CongressyReceiver(
            receiver_type=RECEIVER_TYPE_SUBSCRIPTION,
            identifier=settings.PAGARME_RECIPIENT_ID,
            amount=cgsy_amount,
            chargeback_responsible=True,
            processing_fee_responsible=True,
        )
        receivers.append(cgsy_receiver)

        # Parceiros irão participar do rateamento de inscrições
        partner_receivers = \
            cgsy_receiver.create_and_publish_partners(self.event)

        if partner_receivers:
            for partner_receiver in partner_receivers:
                receivers.append(partner_receiver)

        org_receiver = OrganizerReceiver(
            receiver_type=RECEIVER_TYPE_SUBSCRIPTION,
            identifier=self.organization.recipient_id,
            amount=org_amount,
            transfer_taxes=self.lot.transfer_tax is True,
            chargeback_responsible=True,
            processing_fee_responsible=False,
            installment_result=InstallmentResult(
                calculator=self.installment_calculator,
                amount=self.amount,
                num_installments=int(self.installments),
            ),
        )

        receivers.append(org_receiver)

        return receivers

    def _check_criterias(self):
        """
        Verifica todos os critérios para continuidade dos processos do
        publisher.
        """
        if not hasattr(settings, 'CONGRESSY_INSTALLMENT_INTERESTS_RATE'):
            raise Exception(
                'Configuração "CONGRESSY_INSTALLMENT_INTERESTS_RATE" não'
                ' encontrada em settings.'
            )

        if not hasattr(settings, 'CONGRESSY_MINIMUM_AMOUNT'):
            raise Exception(
                'Configuração "CONGRESSY_MINIMUM_AMOUNT" não encontrada em'
                ' settings.'
            )

        if not hasattr(settings, 'PAGARME_RECIPIENT_ID'):
            raise Exception(
                'Configuração "CONGRESSY_RECIPIENT_ID" não encontrada em'
                ' settings.'
            )

        if settings.DEBUG is False and not self.organization.recipient_id:
            raise Exception(
                'A organização "{} (ID: {})" não possui um'
                ' "recipient_id".'.format(
                    self.organization.name,
                    self.organization.pk,
                )
            )
