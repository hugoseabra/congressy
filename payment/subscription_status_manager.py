from decimal import Decimal

from django.db.models import Sum

from gatheros_subscription.models import Subscription
from payment.helpers import TransactionSubscriptionStatusIntegrator


class SubscriptionStatusManager(object):
    """
        Responsabilidade: processar atualização de inscrição

        Processar atualização constitui em mudar o status da inscrição de
        acordo com um status de transação e o valor da transação que é
        repassado como dependencia
    """

    def __init__(self,
                 transaction_status: str,
                 transaction_value: Decimal,
                 subscription: Subscription) -> None:
        self.transaction_status = transaction_status
        self.transaction_value = transaction_value
        self.subscription = subscription
        super().__init__()

    def _fetch_subscription_status(self):
        # Translate a transaction status to a subscription status.
        integrator = TransactionSubscriptionStatusIntegrator(
            self.transaction_status
        )

        return integrator.integrate()

    def _has_paid_total(self):
        existing_amount = self.subscription.payments.filter(
            paid=True
        ).aggregate(total=Sum('amount'))

        existing_amount = existing_amount['total'] or Decimal(0)
        whole_price = Decimal(0)

        debts = self.subscription.debts.all()
        for debt in debts:
            whole_price += debt.amount

        summed_amount = existing_amount + self.transaction_value

        if summed_amount >= whole_price:
            return True

        return False

    def update_subscription_status(self):
        new_status = self._fetch_subscription_status()

        # Validar se o valor informado somado ao valor já existente já
        # consolida tudo como pago
        if new_status == Subscription.CONFIRMED_STATUS:
            if self._has_paid_total():
                self.subscription.status = new_status
        else:
            self.subscription.status = new_status

            self.subscription.save()
