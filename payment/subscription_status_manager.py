from decimal import Decimal

from gatheros_subscription.models import Subscription
from payment.helpers import TransactionSubscriptionStatusIntegrator


class SubscriptionStatusManager(object):
    """
        Responsabilidade: Estabelecer regras de transição de status de
        inscrição. Caso esta inscrição seja paga, deve respeitar montante para
        saber se a mudança deve ser realizada.
    """

    def __init__(self,
                 transaction_pk: str,
                 transaction_status: str,
                 transaction_value: Decimal,
                 subscription_status: str) -> None:

        self.transaction_pk = transaction_pk
        self.transaction_status = transaction_status
        self.transaction_value = transaction_value
        self.subscription_status = subscription_status
        super().__init__()

    def get_new_status(self,
                       debt: Decimal,
                       existing_payments: Decimal):
        new_status = self._get_subscription_status()

        # Validar se o valor informado somado ao valor já existente já
        # consolida tudo como pago
        if new_status == Subscription.CONFIRMED_STATUS and \
                self.transaction_value > Decimal(0):

            if self._has_paid_total(debt, existing_payments):
                return new_status

            else:

                return self.subscription_status

        return new_status

    def _get_subscription_status(self):
        # Translate a transaction status to a subscription status.
        integrator = TransactionSubscriptionStatusIntegrator(
            transaction_state=self.transaction_status,
            transaction_pk=self.transaction_pk,
        )

        return integrator.integrate()

    def _has_paid_total(self, debt: Decimal, existing_amount: Decimal):

        existing_amount = existing_amount or Decimal(0)
        whole_price = debt or Decimal(0)

        summed_amount = existing_amount + self.transaction_value

        if summed_amount >= whole_price:
            return True

        return False
