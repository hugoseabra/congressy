from payment.exception import PostbackNotificationError
from payment.models import Transaction
from .boleto_notification import BoletoPaymentNotification
from .credit_card_notification import CreditCardPaymentNotification


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
