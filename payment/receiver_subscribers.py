"""
Gerenciamento de coleções de Receivers que serão usados para diferentes
operações de processamento para obter regras de rateamento de pagamento.
"""
from collections import OrderedDict
from datetime import date
from decimal import Decimal

from django.conf import settings

from gatheros_subscription.models import Subscription
from payment import receivers, exception
from payment.installments import Calculator, InstallmentResult
from payment.payable.credit_card import get_payables

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
        diff_amount = round(diff_amount, 2)

        if diff_amount > 0.02:
            raise exception.ReceiverTotalAmountExceeded(
                'O valor dos recebedores já ultrapassa o valor a ser'
                ' transacionado. Valor da transação: {}. Valor somado'
                ' dos recebedores: {}.'.format(
                    round(self.amount, 2),
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

        assert isinstance(amount, Decimal)
        self.amount = amount
        self.installments = installments
        self.organization = subscription.event.organization

        self._check_criterias()

        self.interests_rate = Decimal(
            float(settings.CONGRESSY_INSTALLMENT_INTERESTS_RATE) / 100
        )

        lot = self.subscription.lot

        self.installment_calculator = Calculator(
            interests_rate=self.interests_rate,
            total_installments=int(lot.installment_limit),
            free_installments=int(lot.num_install_interest_absortion),
        )

    def create_and_publish_subscription(self):
        """
        Cria e publica recebedores que irã participar do rateamente de uma
        inscrição.
        """
        event = self.subscription.event
        lot = self.subscription.lot

        # ==== CONGRESSY AMOUNT
        # Valor proporcional da Congressy, independente de transferência ou
        # não de taxas. O valor é calculado em cima do preço informado pelo
        # organizador ao criar o lote.
        cgsy_percent = Decimal(float(event.congressy_percent) / 100)

        if self.transaction_type == 'boleto' and self.installments > 1:
            # Por causa do parcalamento de boletos, o valor chegando de fora
            # pode ser menor do que o preço líquido do lote que a Congressy
            # deve captar de acrodo com o percentual.
            cgsy_amount = (lot.price / self.installments) * cgsy_percent

        else:
            cgsy_amount = lot.price * cgsy_percent

        minimum_amount = Decimal(
            getattr(settings, 'CONGRESSY_MINIMUM_AMOUNT', 0)
        )

        # Mínimo aplicável apenas para inscrição.
        if minimum_amount and cgsy_amount < minimum_amount:
            cgsy_amount = minimum_amount

        # ==== ORGANIZATION AMOUNT
        # Se houve transferência de taxas, o valor da Congressy já está
        # no montante da transação.
        if lot.transfer_tax is True:
            # Se há transferência, o organizador sempre receberá o valor
            # informado no lote.
            if self.transaction_type == 'boleto' and self.installments > 1:
                org_amount = self.amount
            else:
                org_amount = lot.price

        else:
            # Caso, ele assumirá o valor da Congressy e o montante a ser
            # transacionado já está com o valor sem as taxas da Congressy.
            if self.transaction_type == 'boleto' and self.installments > 1:
                org_amount = self.amount - cgsy_amount
            else:
                org_amount = lot.price - cgsy_amount

        # Verifica se há atividades extras.
        for service in self.subscription.subscription_services.all():
            price_diff = service.optional.price - service.optional.liquid_price
            cgsy_amount += price_diff

        # Verifica se há opcionais.
        for product in self.subscription.subscription_products.all():
            price_diff = product.optional.price - product.optional.liquid_price
            cgsy_amount += price_diff

        # Verifica se há atividades extras.
        for service in self.subscription.subscription_services.all():
            org_amount += service.optional.liquid_price

        # Verifica se há opcionais.
        for product in self.subscription.subscription_products.all():
            org_amount += product.optional.liquid_price

        # Soma do montante distribuído entre as partes.
        total = Decimal(org_amount + cgsy_amount)

        if round(Decimal(self.amount), 2) > round(total, 2):
            # A diferença que há no montante a ser transacionado irá para a
            # Congressy, por já estar embutidas taxas e juros de parcelamento,
            # se houver.
            cgsy_amount += Decimal(self.amount - total)

        # Organização irá receber o valor até aqui. Qualquer valor adicionado
        # devido a cobrança de juros e taxas do pagar.me, será apenas uma
        # adequação para que o valor final seja exatamente esse valor.
        org_liquid_amount = org_amount

        if self.installments > 1:
            # Se o organizador assumiu juros de parcelamento, o montante a ser
            # transacionado estará sem o valor de juros de parcelamento. Então,
            # vamos recalcula-los.
            free_installments = lot.num_install_interest_absortion
            if 1 < int(self.installments) <= int(free_installments):
                interests_amount = \
                    self.installment_calculator.get_absorbed_interests_amount(
                        amount=Decimal(self.amount),
                        installments=self.installments,
                    )

                if interests_amount > 0:
                    # Retira valor e juros assumido e o coloca sob competência
                    # da Congressy.
                    org_amount -= interests_amount
                    cgsy_amount += interests_amount

            if self.transaction_type == 'credit_card' \
                    and self.installments > 1:
                # Agora vamos verificar possíveis valores de taxa de
                # antecipação paga pelo participante no parcelamento e repassar
                # à organização para quando houver a antecipação, o valor final
                # ser o valor líquido esperado pela organização
                payables = get_payables(
                    recipient_id=self.organization.recipient_id,
                    transaction_amount=self.amount,
                    transaction_date=date.today(),
                    payable_amount=org_amount,
                    installments=self.installments,
                    fee_percent=None,
                    antecipation_fee_percent=Decimal(1.99),
                )

                antecipation_fee = 0
                for payable in payables:
                    antecipation_fee += payable.get_antecipation_amount()

                if antecipation_fee:
                    org_amount += antecipation_fee
                    cgsy_amount -= antecipation_fee

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

        # Parceiros irão participar do rateamento de inscrições
        partner_receivers = \
            cgsy_receiver.create_and_publish_partners(self.subscription)

        if partner_receivers:
            for partner_receiver in partner_receivers:
                self.receiver_subscriber.publish(partner_receiver)

        self.receiver_subscriber.publish(cgsy_receiver)

        org_receiver = receivers.OrganizerReceiver(
            type=RECEIVER_TYPE_SUBSCRIPTION,
            id=self.organization.recipient_id,
            amount=org_amount,
            liquid_amount=org_liquid_amount,
            transfer_taxes=lot.transfer_tax is True,
            chargeback_responsible=True,
            processing_fee_responsible=False,
            installment_result=InstallmentResult(
                calculator=self.installment_calculator,
                amount=Decimal(self.amount),
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
