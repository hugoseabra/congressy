from gatheros_subscription.models import Subscription
from mailer.services import (
    notify_new_user_and_paid_subscription_boleto,
    notify_paid_subscription_boleto,
)
from payment.exception import PostbackNotificationError
from payment.models import Transaction


class BoletoPaymentNotification(object):
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
        pass

    def _notify_confirmed_subscription(self):
        if self.transaction.status != Transaction.PAID:
            raise PostbackNotificationError(
                transaction_pk=str(self.transaction.pk),
                message="Inscrição confirmada não pode ter uma transação com "
                        "status diferente de pago. Status da transação: {}"
                        "".format(self.transaction.status)
            )

        if self.subscription.notified is False:
            notify_new_user_and_paid_subscription_boleto(
                self.subscription.event,
                self.transaction,
            )
        else:
            notify_paid_subscription_boleto(
                self.subscription.event,
                self.transaction,
            )
