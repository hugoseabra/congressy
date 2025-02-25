from gatheros_subscription.models import Subscription
from mailer.services import (
    notify_new_user_and_paid_subscription_credit_card_with_discrepancy,
    notify_chargedback_subscription,
    notify_new_user_and_paid_subscription_credit_card,
    notify_new_user_and_refused_subscription_credit_card,
    notify_new_user_and_unpaid_subscription_credit_card,
    notify_pending_refund_subscription,
    notify_refunded_subscription_credit_card,
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
        elif self.subscription.status == Subscription.CONFIRMED_STATUS:
            self._notify_confirmed_subscription()
        else:
            raise PostbackNotificationError(
                transaction_pk=str(self.transaction.pk),
                message="Status de inscrição desconhecido para "
                        "notificar: {}".format(self.subscription.status),
            )

    def _notify_pending_subscription(self):

        if self.transaction.status == Transaction.PAID:

            notify_new_user_and_paid_subscription_credit_card_with_discrepancy(
                self.subscription.event,
                self.transaction,
            )

        elif self.transaction.status == Transaction.WAITING_PAYMENT:

            notify_new_user_and_unpaid_subscription_credit_card(
                self.subscription.event,
                self.transaction,
            )

        elif self.transaction.status == Transaction.REFUNDED:

            notify_refunded_subscription_credit_card(
                self.subscription.event,
                self.transaction,
            )

        elif self.transaction.status == Transaction.PENDING_REFUND:

            notify_pending_refund_subscription(
                self.subscription.event,
                self.transaction,
            )

        elif self.transaction.status == Transaction.REFUSED:

            notify_new_user_and_refused_subscription_credit_card(
                self.subscription.event,
                self.transaction,
            )

        elif self.transaction.status == Transaction.CHARGEDBACK:
            notify_chargedback_subscription(
                self.subscription.event,
                self.transaction,
            )

        else:
            raise PostbackNotificationError(
                message="Status de transação desconhecido para notificar "
                        "inscrição pendente: {}"
                        "".format(self.transaction.status),
                transaction_pk=str(self.transaction.pk),
            )

    def _notify_confirmed_subscription(self):
        if self.transaction.status == Transaction.PAID:
            notify_new_user_and_paid_subscription_credit_card(
                self.subscription.event,
                self.transaction,
            )
        elif self.transaction.status == Transaction.CHARGEDBACK:
            notify_chargedback_subscription(
                self.subscription.event,
                self.transaction,
            )
        else:
            raise PostbackNotificationError(
                message="Status de transação desconhecido para notificar "
                        "inscrição confirmada: {}"
                        "".format(self.transaction.status),
                transaction_pk=str(self.transaction.pk),
            )
