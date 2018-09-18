from datetime import datetime

from gatheros_subscription.models import Subscription
from payment.models import Transaction


class CurrentSubscriptionState(object):
    def __init__(self, subscription: Subscription) -> None:
        self.subscription = subscription
        self.person = subscription.person

        self.transactions = self._get_transactions()

        self.payments = self._get_payments()

        # As vezes a inscrição não possui lote por estar em processo de
        # finalização de inscrição.
        self.lot = subscription.lot

    def _get_transactions(self):

        all_transactions = self.subscription.transactions.filter(
            lot=self.subscription.lot
        )

        now = datetime.now().date()

        transactions = []

        for transaction in all_transactions:
            if transaction.boleto_expiration_date:
                if transaction.boleto_expiration_date > now:
                    transactions.append(transaction)
            else:
                transactions.append(transaction)

        return transactions

    def _get_payments(self):
        if not self.subscription:
            return []

        payments = []
        for transaction in self.transactions:
            if transaction.status == Transaction.PAID:
                payments.append(transaction)

        return payments

    def has_transactions(self):
        return len(self.transactions) > 0

    def has_payments(self):
        return len(self.payments) > 0

    def has_paid_optionals(self):
        """ Retorna se evento possui algum lote pago. """

        prods_qs = self.subscription.subscription_products
        servs_qs = self.subscription.subscription_products
        has_prods = prods_qs.filter(optional_price__gt=0).count() > 0
        has_servs = servs_qs.filter(optional_price__gt=0).count() > 0

        return has_prods is True or has_servs is True
