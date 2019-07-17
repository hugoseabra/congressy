"""
Gerenciamento de coleções de Receivers que serão usados para diferentes
operações de processamento para obter regras de rateamento de pagamento.
"""
from collections import OrderedDict
from decimal import Decimal

from django.conf import settings

from gatheros_subscription.models import Subscription
from payment import receivers, exception
from payment.installments import Calculator, InstallmentResult

from ticket.congressy import CongressyPlan

RECEIVER_TYPE_SUBSCRIPTION = 'receiver_subscription'
RECEIVER_TYPE_PRODUCT = 'receiver_product'
RECEIVER_TYPE_SERVICE = 'receiver_service'


class ReceiverSubscriber(object):
    """
    Receber inscrições de objetos Receiver para operações diversas.
    """

    def __init__(self, amount: Decimal) -> None:
        assert isinstance(amount, Decimal)

        self.receivers = OrderedDict()

        self.amount = amount
        self.added_amount = Decimal(0)

    def publish(self, receiver: receivers.Receiver):
        if not receiver.id:
            raise exception.RecipientError(
                'Um recebedor do tipo "{}" não possui ID.'.format(
                    receiver.type
                )
            )

        if receiver.id in self.receivers:
            raise exception.ReceiverAlreadyPublishedError(
                'Você não pode publicar recebedor com id "{}" porque ele já'
                ' foi publicado anteriormente.'.format(receiver.id)
            )

        self.added_amount += receiver.amount

        diff_amount = self.added_amount - self.amount
        diff_amount = round(Decimal(diff_amount), 2)

        if diff_amount > 0.02:
            raise exception.ReceiverTotalAmountExceeded(
                'O valor dos recebedores já ultrapassa o valor a ser'
                ' transacionado. Valor da transação: {}. Valor somado'
                ' dos recebedores: {}.'.format(
                    round(Decimal(self.amount), 2),
                    round(self.added_amount, 2),
                )
            )

        self.receivers[receiver.id] = receiver


class ReceiverPublisher(object):
    """
    Publicador de Recebedores de acordo com inscrição informada.
    """

    def __init__(self,
                 receiver_subscriber: ReceiverSubscriber,
                 transaction_type: str,
                 subscription: Subscription,
                 amount: Decimal,
                 installments: int) -> None:
        self.receiver_subscriber = receiver_subscriber
        self.transaction_type = transaction_type
        self.subscription = subscription

        self.amount = amount
        self.installments = installments

        self.ticket = subscription.ticket
        self.event = subscription.event
        self.organization = self.event.organization

        self._check_criterias()

        self.interests_rate = Decimal(
            float(settings.CONGRESSY_INSTALLMENT_INTERESTS_RATE) / 100
        )

        self.installment_calculator = Calculator(
            interests_rate=self.interests_rate,
            total_installments=10,
            free_installments=self.ticket.free_installments,
        )

    def create_and_publish_subscription(self):
        """
        Cria e publica recebedores que irã participar do rateamente de uma
        inscrição.
        """
        sub_plan = CongressyPlan(
            amount=self.ticket.get_subscriber_price(),
            percent=Decimal(self.event.congressy_percent) / 100
        )

        cgsy_amount = sub_plan.get_congressy_amount()
        org_amount = sub_plan.get_organizer_amount()

        # Verifica se há atividades extras.
        for sub_serv in self.subscription.subscription_services.all():
            optional = sub_serv.optional

            serv_plan = CongressyPlan(
                amount=optional.price,
                percent=Decimal(self.event.congressy_percent) / 100
            )
            cgsy_amount += serv_plan.get_congressy_amount()
            org_amount += serv_plan.get_organizer_amount()

        # Verifica se há opcionais.
        for sub_prod in self.subscription.subscription_products.all():
            optional = sub_prod.optional

            prod_plan = CongressyPlan(
                amount=optional.price,
                percent=Decimal(self.event.congressy_percent) / 100
            )
            cgsy_amount += prod_plan.get_congressy_amount()
            org_amount += prod_plan.get_organizer_amount()


        # Soma do montante distribuído entre as partes.
        total = Decimal(org_amount + cgsy_amount)

        if round(Decimal(self.amount), 2) > round(total, 2):
            # A diferença que há no montante a ser transacionado irá para a
            # Congressy, por já estar embutidas taxas e juros de parcelamento,
            # se houver.
            cgsy_amount += Decimal(self.amount - total)

        if self.installments > 1:
            # Se o organizador assumiu juros de parcelamento, o montante a ser
            # transacionado estará sem o valor de juros de parcelamento. Então,
            # vamos recalcula-los.
            free_installments = self.ticket.free_installments
            if 1 < self.installments <= free_installments:
                free_installment_plan = CongressyPlan(
                    amount=self.amount,
                    percent=Decimal(self.event.congressy_percent) / 100
                )
                calculator = free_installment_plan.get_installment(
                    num_parts=self.installments,
                    free_parts=free_installments,
                )
                interests = calculator.get_installment_interests_amount()

                if interests > 0:
                    # Retira valor e juros assumido e o coloca sob competência
                    # da Congressy.
                    org_amount -= interests
                    cgsy_amount += interests

        # total novamente.
        total = Decimal(org_amount + cgsy_amount)

        # Depois de todos os valores distribuídos, o valor entre a Congressy
        # e organizador tem de ser de acordo com o montante a ser
        # transacionado.
        assert round(total, 2) == round(Decimal(self.amount), 2), \
            "total splitable amount: {}. Amount: {}".format(
                round(total, 2),
                round(Decimal(self.amount), 2)
            )

        # ==== RECEIVERS
        cgsy_receiver = receivers.CongressyReceiver(
            type=RECEIVER_TYPE_SUBSCRIPTION,
            id=settings.PAGARME_RECIPIENT_ID,
            amount=cgsy_amount,
            chargeback_responsible=True,
            processing_fee_responsible=True,
        )

        self.receiver_subscriber.publish(cgsy_receiver)

        # Parceiros irão participar do rateamento de inscrições
        partner_receivers = \
            cgsy_receiver.create_and_publish_partners(self.subscription)

        if partner_receivers:
            for partner_receiver in partner_receivers:
                self.receiver_subscriber.publish(partner_receiver)

        org_receiver = receivers.OrganizerReceiver(
            type=RECEIVER_TYPE_SUBSCRIPTION,
            id=self.organization.recipient_id,
            amount=org_amount,
            transfer_taxes=self.event.transfer_tax is True,
            chargeback_responsible=True,
            processing_fee_responsible=False,
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
        # if self.subscription.free is True:
        #     raise Exception(
        #         'A inscrição "{}" é gratuita e não pode possuir um'
        #         ' recebedor.'.format(self.subscription.pk)
        #     )

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
