"""
Gerenciamento de coleções de Receivers que serão usados para diferentes
operações de processamento para obter regras de rateamento de pagamento.
"""
from decimal import Decimal
from collections import OrderedDict

from django.conf import settings

from . import receivers, exceptions, constants
from .installments import Calculator, InstallmentResult
from gatheros_subscription.models import Subscription


class ReceiverSubscriber(object):
    """
    Receber inscrições de objetos Receiver para operações diversas.
    """

    def __init__(self):
        self.receivers = OrderedDict()

    def publish(self, receiver: receivers.Receiver):
        if receiver.id in self.receivers:
            raise exceptions.ReceiverAlreadyPublishedError(
                'Você não pode publicar recebedor com id "{}" porque ele já'
                ' foi publicado anteriormente.'.format(receiver.id)
            )

        self.receivers[receiver.id] = receivers

class ReceiverPublisher(object):
    """
    Publicador de Recebedores de acordo com inscrição informada.
    """
    def __init__(self,
                 receiver_subscriber: ReceiverSubscriber,
                 subscription: Subscription,
                 amount: Decimal,
                 installments: int) -> None:
        self.receiver_subscriber = receiver_subscriber
        self.subscription = subscription

        self.amount = amount
        self.installments = installments
        self.organization = subscription.event.organization

        self._check_criterias()

        self.interests_rate = Decimal(
            float(settings.CONGRESSY_INSTALLMENT_INTERESTS_RATE) / 100
        )

        self.installment_calculator = Calculator(
            interests_rate=interests_rate,
            total_installments=int(self.lot.installment_limit),
            free_installments=int(self.lot.num_install_interest_absortion),
        )


    def create_and_publish_subscription(self):
        """
        Cria e publica recebedores que irã participar do rateamente de uma
        inscrição.
        """
        event = self.subscription.event
        lot = self.subscription.lot

        # ==== CONGRESSY AMOUNT
        cgsy_percent = Decimal(float(event.congressy_percent) / 100)

        # Valor proporcional da Congressy, independente de transferência ou
        # não de taxas. O valor é calculado em cima do preço informado pelo
        # organizador ao criar o lote.
        cgsy_amount = lot.price * cgsy_percent

        minimum_amount = Decimal(
            getattr(settings, 'CONGRESSY_MINIMUM_AMOUNT', 0)
        )
        if minimum_amount and cgsy_amount < minimum_amount:
            cgsy_amount = minimum_amount


        # ==== ORGANIZATION AMOUNT
        org_amount = amount - cgsy_amount

        free_installments = self.lot.num_install_interest_absortion
        if self.installments > 1 and self.installments <= free_installments:
            interests_amount = \
                self.installment_calculator.get_absorbed_interests_amount(
                    amount=self.amount,
                    installments=self.installments,
                )

            # Retira valor e juros assumido e o coloca sob competência da
            # Congressy.
            org_amount -= interests_amount
            cgsy_amount += interests_amount

        # ==== RECEIVERS
        cgsy_receiver = receivers.CongressyReceiver(
            type=constants.RECEIVER_TYPE_SUBSCRIPTION,
            id=settings.CONGRESSY_RECIPIENT_ID,
            amount=cgsy_amount,
            chargeback_responsible=True,
            processing_fee_responsible=True,
        )

        self.receiver_subscriber.publish(cgsy_receiver)

        # Parceiros irão participar do rateamento de inscrições
        cgsy_receiver.create_and_publish_partners(self.receiver_subscriber)

        org_receiver = receivers.OrganizerReceiver(
            type=constants.RECEIVER_TYPE_SUBSCRIPTION,
            id=self.organization.recipient_id,
            amount=cgsy_amount,
            transfer_taxes=self.lot.transfer_tax is True,
            chargeback_responsible=True,
            processing_fee_responsible=True,
            installment_result=InstallmentResult(
                calculator=self.installment_calculator,
                amount=self.amount,
                num_installments=int(self.installments),
            ),
        )

        self.receiver_subscriber.publish(org_receiver)


    def create_and_publish_products(self):
        """
        Cria e publica recebedores que irã participar do rateamente de
        opcionais baseados em informações de inscrição.
        """
        pass

    def create_and_publish_services(self):
        """
        Cria e publica recebedores que irã participar do rateamente de
        atividades extras baseados em informações de inscrição.
        """
        pass

    def _create_and_publish_product(self, optional_product):
        """
        Cria e publica recebedores que irã participar do rateamente de uma
        opcionais baseados em informações de inscrição.
        """
        pass

    def _create_and_publish_service(self, optional_service):
        """
        Cria e publica recebedores que irã participar do rateamente de uma
        atividade extra baseados em informações de inscrição.
        """
        pass


    def _check_criterias(self):
        """
        Verifica todos os critérios para continuidade dos processos do
        publisher.
        """
        if subscription.free is True:
            raise Exception(
                'A inscrição "{}" é gratuita e não pode possuir um'
                ' receber.'.format(subscription.pk)
            )

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

        if not self.organization.recipient_id:
            raise Exception(
                'A organização "{} (ID: {})" não possui um'
                ' "recipient_id".'.format(
                    self.organization.name,
                    self.organization.pk,
                )
            )
