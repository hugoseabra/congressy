from gatheros_subscription.models import Subscription
from payment.exception import TransactionStatusIntegratorError


class TransactionSubscriptionStatusIntegrator:

    awaiting_status = [
        'processing',
        'waiting_payment',
        'chargeback'
        'pending_refund',
    ]

    confirmed_status = [
        'paid'
    ]

    cancelled_status = [
        'refused',
        'refunded',
    ]

    def __init__(self, transaction_status):
        self.transaction_status = transaction_status

    def integrate(self):

        if self.transaction_status in self.awaiting_status:
            return Subscription.AWAITING_STATUS
        elif self.transaction_status in self.confirmed_status:
            return Subscription.CONFIRMED_STATUS
        elif self.transaction_status in self.cancelled_status:
            return Subscription.CANCELED_STATUS
        else:
            raise TransactionStatusIntegratorError(
                'Unknown status given.')
