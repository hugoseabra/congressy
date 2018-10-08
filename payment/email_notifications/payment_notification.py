from gatheros_subscription.models import Subscription
from payment.exception import PostbackNotificationError
from payment.models import Transaction
from .boleto_notification import BoletoPaymentNotification


class PaymentNotification(object):

    def __init__(self, transaction: Transaction) -> None:
        self.transaction = transaction
        super().__init__()

    def notify(self):

        if self.transaction.type == Transaction.BOLETO:
            BoletoPaymentNotification(
                transaction=self.transaction,
            ).notify()

        elif self.transaction.type == Transaction.CREDIT_CARD:
            CreditCardPaymentNotification(
                transaction=self.transaction,
            ).notify()
        else:
            raise PostbackNotificationError(
                transaction_pk=str(self.transaction.pk),
                message="Tipo de transação desconhecida para a transação: {}"
                        "".format(str(self.transaction.pk))
            )


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
        pass

    def _notify_confirmed_subscription(self):
        pass
