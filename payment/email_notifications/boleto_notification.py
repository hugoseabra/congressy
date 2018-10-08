from gatheros_subscription.models import Subscription
from mailer.services import (
    notify_paid_with_incoming_installment,
    notify_unpaid_installment,
    notify_installment_with_discrepancy,
    notify_new_unpaid_subscription_boleto,
    notify_new_user_and_paid_subscription_boleto,
    notify_new_user_and_refused_subscription_boleto,
    notify_new_user_and_unpaid_subscription_boleto,
    notify_paid_subscription_boleto, notify_refunded_subscription_boleto,
    notify_pending_refund_subscription_boleto,
)
from payment.exception import PostbackNotificationError
from payment.models import Transaction


class BoletoPaymentNotification(object):
    def __init__(self, transaction: Transaction) -> None:
        self.transaction = transaction
        self.subscription = transaction.subscription
        super().__init__()

    def notify(self):

        if self.subscription == Subscription.CONFIRMED_STATUS:
            self._notify_confirmed_subscription()
        elif self.subscription.status == Subscription.AWAITING_STATUS:
            self._notify_pending_subscription()

        else:
            raise PostbackNotificationError(
                transaction_pk=str(self.transaction.pk),
                message="Status de inscrição desconhecido para notificar: {}"
                        "".format(self.subscription.status)
            )

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

    def _notify_pending_subscription(self):

        if self.transaction.status == Transaction.PAID:

            self.__notify_pending_sub_paid_transaction()

        elif self.transaction.status == Transaction.WAITING_PAYMENT:

            self.__notify_pending_sub_pending_transaction()

        elif self.transaction.status == Transaction.REFUNDED:

            notify_refunded_subscription_boleto(
                self.subscription.event,
                self.transaction,
            )

        elif self.transaction.status == Transaction.PENDING_REFUND:

            notify_pending_refund_subscription_boleto(
                self.subscription.event,
                self.transaction,
            )

        elif self.transaction.status == Transaction.REFUSED:

            notify_new_user_and_refused_subscription_boleto(
                self.subscription.event,
                self.transaction,
            )

        else:

            raise PostbackNotificationError(
                transaction_pk=str(self.transaction.pk),
                message="Status de transação desconhecido para notificar "
                        "inscrição pendente: {}"
                        "".format(self.transaction.status)
            )

    def __notify_pending_sub_pending_transaction(self):
        if self.transaction.installments == 1:

            if self.subscription.notified is False:
                notify_new_user_and_unpaid_subscription_boleto(
                    self.subscription.event,
                    self.transaction,
                )
            else:
                notify_new_unpaid_subscription_boleto(
                    self.subscription.event,
                    self.transaction,
                )
        else:

            notify_unpaid_installment(
                self.subscription.event,
                self.transaction,
            )

    def __notify_pending_sub_paid_transaction(self):

        if self.transaction.installments == 1:
            notify_installment_with_discrepancy(
                self.subscription.event,
                self.transaction,
            )
        else:
            notify_paid_with_incoming_installment(
                self.subscription.event,
                self.transaction,
            )
