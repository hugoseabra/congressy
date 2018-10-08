from gatheros_subscription.models import Subscription
from mailer.services import (
    notify_new_user_and_paid_subscription_credit_card,
    notify_new_user_and_paid_subscription_credit_card_with_discrepancy,
)
from payment.exception import PostbackNotificationError
from payment.models import Transaction


class CreditCardPaymentNotification(object):

    def __init__(self, transaction: Transaction) -> None:
        self.transaction = transaction
        self.subscription = transaction.subscription
        super().__init__()

    def notify(self):

        if self.subscription.status == Subscription.AWAITING_STATUS:
            self._notify_pending_subscription()
        elif self.subscription == Subscription.CONFIRMED_STATUS:
            self._notify_confirmed_subscription()
        else:
            raise PostbackNotificationError(
                transaction_pk=str(self.transaction.pk),
                message="Status de inscrição desconhecido para notificar: {}"
                        "".format(self.subscription.status)
            )

    def _notify_pending_subscription(self):
        notify_new_user_and_paid_subscription_credit_card_with_discrepancy(
            self.subscription.event,
            self.transaction,
        )

    def _notify_confirmed_subscription(self):
        notify_new_user_and_paid_subscription_credit_card(
            self.subscription.event,
            self.transaction,
        )
