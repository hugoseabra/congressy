from mailer import exception as mailer_notification
from mailer.services import (
    notify_chargedback_subscription,
    notify_new_paid_subscription_credit_card,
    notify_new_refused_subscription_boleto,
    notify_new_refused_subscription_credit_card,
    notify_new_unpaid_subscription_boleto,
    notify_new_unpaid_subscription_credit_card,
    notify_new_user_and_paid_subscription_boleto,
    notify_new_user_and_paid_subscription_credit_card,
    notify_new_user_and_refused_subscription_boleto,
    notify_new_user_and_refused_subscription_credit_card,
    notify_new_user_and_unpaid_subscription_boleto,
    notify_new_user_and_unpaid_subscription_credit_card,
    notify_paid_subscription_boleto, notify_refunded_subscription_boleto,
    notify_pending_refund_subscription_boleto,
    notify_refunded_subscription_credit_card,
)
from payment.models import Transaction


class PaymentNotification(object):

    def __init__(self, transaction) -> None:
        self.transaction = transaction
        super().__init__()

    def notify(self, new_status: str):

        subscription = self.transaction.subscription
        is_new_subscription = subscription.notified is False
        event = subscription.event
        sub_user = subscription.person.user

        boleto_notification = BoletoPaymentNotification()
        credit_card_notification = CreditCardPaymentNotification()

        if is_new_subscription:

            if self.transaction.type == Transaction.BOLETO:

                boleto_notification.notify_new_subscription(
                    transaction=self.transaction,
                    new_status=new_status,
                )

            elif self.transaction.type == Transaction.CREDIT_CARD:

                credit_card_notification.notify_new_subscription(
                    transaction=self.transaction,
                    new_status=new_status,
                )

            else:

                msg = 'Notificação de transação de nova inscrição não'
                msg += ' pôde ser realizada devido ao seguinte erro:'
                msg += ' método de pagamento desconhecido para'
                msg += ' notificação - "{}". Evento: {}. Inscrição:'
                msg += ' {} ({} - {} - {}). Transaction {}. '
                msg += msg.format(
                    new_status,
                    event.name,
                    sub_user.get_full_name(),
                    sub_user.pk,
                    sub_user.email,
                    self.transaction.subscription.pk,
                    self.transaction.pk,
                )

                raise mailer_notification.NotifcationError(msg)

        else:  # Não é nova inscrição

            if self.transaction.type == Transaction.BOLETO:

                boleto_notification.notify_existing_subscription(
                    transaction=self.transaction,
                    new_status=new_status,
                )

            elif self.transaction.type == Transaction.CREDIT_CARD:
                credit_card_notification.notify_existing_subscription(
                    transaction=self.transaction,
                    new_status=new_status,
                )

            else:
                msg = 'Notificação de transação de inscrição não pôde ser'
                msg += ' realizada devido ao seguinte erro: método de'
                msg += ' pagamento desconhecido para notificação - "{}".'
                msg += ' Evento: {}. Inscrição: {} ({} - {} - {}).'
                msg += ' Transaction {}.'.format(
                    new_status,
                    event.name,
                    sub_user.get_full_name(),
                    sub_user.pk,
                    sub_user.email,
                    self.transaction.subscription.pk,
                    self.transaction.pk,
                )

                raise mailer_notification.NotifcationError(msg)


class BoletoPaymentNotification(object):

    # noinspection PyMethodMayBeStatic
    def notify_new_subscription(self, transaction, new_status: str):

        subscription = transaction.subscription
        event = subscription.event

        sub_user = subscription.person.user

        is_paid = new_status == Transaction.PAID
        is_refused = new_status == Transaction.REFUSED
        is_refunded = new_status == Transaction.REFUNDED
        is_waiting = new_status == Transaction.WAITING_PAYMENT
        is_chargedback = new_status == Transaction.CHARGEDBACK

        if is_waiting:
            # Novas inscrições nunca estão pagas.
            notify_new_user_and_unpaid_subscription_boleto(
                event,
                transaction
            )

        elif is_paid:
            # Se não é status inicial, certamente o boleto foi]
            # pago.
            notify_new_user_and_paid_subscription_boleto(
                event,
                transaction
            )

        elif is_refused:
            # Quando a emissão do boleto falha por algum motivo.
            notify_new_user_and_refused_subscription_boleto(
                event,
                transaction
            )

        elif is_refunded:
            notify_refunded_subscription_boleto(event,
                                                transaction)

        elif is_chargedback:

            notify_chargedback_subscription(event, transaction)

        else:
            msg = 'Notificação de transação de boleto de nova' \
                  ' inscrição não pôde ser realizada devido ao' \
                  ' seguinte erro: status desconhecido para' \
                  ' notificação - "{}". Evento: {}. Inscrição:' \
                  ' {} ({} - {} - {}). Transaction {}.'.format(
                new_status,
                event.name,
                sub_user.get_full_name(),
                sub_user.pk,
                sub_user.email,
                transaction.subscription.pk,
                transaction.pk,
            )

            raise mailer_notification.NotifcationError(msg)

    # noinspection PyMethodMayBeStatic
    def notify_existing_subscription(self, transaction, new_status: str):

        subscription = transaction.subscription
        event = subscription.event

        sub_user = subscription.person.user

        is_paid = new_status == Transaction.PAID
        is_refused = new_status == Transaction.REFUSED
        is_refunded = new_status == Transaction.REFUNDED
        is_pending_refund = new_status == Transaction.PENDING_REFUND
        is_waiting = new_status == Transaction.WAITING_PAYMENT

        if is_waiting:
            notify_new_unpaid_subscription_boleto(
                event,
                transaction
            )

            # Se não é status inicial, certamente o boleto foi pago.
        elif is_paid:
            notify_paid_subscription_boleto(event, transaction)

        elif is_refused:
            # Possivelmente por alguma falha.
            notify_new_refused_subscription_boleto(
                event,
                transaction
            )

        elif is_refunded:
            notify_refunded_subscription_boleto(event,
                                                transaction)

        elif is_pending_refund:
            notify_pending_refund_subscription_boleto(
                event,
                transaction
            )

        else:
            msg = 'Notificação de transação de boleto de inscrição'
            msg += ' não pôde ser realizada devido ao seguinte'
            msg += ' erro: status desconhecido para notificação'
            msg += '  - "{}".'
            msg += ' Evento: {}. Inscrição: {} ({} - {} - {}).'
            msg += ' Transaction {}.'
            msg += msg.format(
                new_status,
                event.name,
                sub_user.get_full_name(),
                sub_user.pk,
                sub_user.email,
                transaction.subscription.pk,
                transaction.pk,
            )

            raise mailer_notification.NotifcationError(msg)


class CreditCardPaymentNotification(object):

    # noinspection PyMethodMayBeStatic
    def notify_new_subscription(self, transaction, new_status: str):
        subscription = transaction.subscription
        event = subscription.event

        sub_user = subscription.person.user

        is_paid = new_status == Transaction.PAID
        is_refused = new_status == Transaction.REFUSED
        is_refunded = new_status == Transaction.REFUNDED
        is_waiting = new_status == Transaction.WAITING_PAYMENT
        is_chargedback = new_status == Transaction.CHARGEDBACK

        if is_waiting:
            # Pode acontecer um delay no pagamento de cartão
            notify_new_user_and_unpaid_subscription_credit_card(
                event,
                transaction
            )

        elif is_paid:
            # Se não é status inicial, certamente o boleto foi
            # pago.
            notify_new_user_and_paid_subscription_credit_card(
                event,
                transaction
            )

        elif is_refused:
            notify_new_user_and_refused_subscription_credit_card(
                event,
                transaction
            )

        elif is_refunded:
            notify_refunded_subscription_credit_card(
                event,
                transaction
            )

        elif is_chargedback:

            notify_chargedback_subscription(event, transaction)

        else:

            msg = 'Notificação de transação de cartão de crédito'
            msg += ' de nova inscrição não pôde ser realizada'
            msg += ' devido ao seguinte erro: status desconhecido'
            msg += ' para notificação - "{}". Evento: {}.'
            msg += ' Inscrição: {} ({} - {} - {}).'
            msg += ' Transaction {}.'
            msg += msg.format(
                new_status,
                event.name,
                sub_user.get_full_name(),
                sub_user.pk,
                sub_user.email,
                transaction.subscription.pk,
                transaction.pk,
            )

            raise mailer_notification.NotifcationError(msg)

    # noinspection PyMethodMayBeStatic
    def notify_existing_subscription(self, transaction, new_status: str):

        subscription = transaction.subscription
        event = subscription.event

        sub_user = subscription.person.user

        is_paid = new_status == Transaction.PAID
        is_refused = new_status == Transaction.REFUSED
        is_refunded = new_status == Transaction.REFUNDED
        is_waiting = new_status == Transaction.WAITING_PAYMENT

        if is_waiting:
            # Pode acontecer um delay no pagamento de cartão
            notify_new_unpaid_subscription_credit_card(
                event,
                transaction
            )

        elif is_paid:
            # Se não é status inicial, certamente o boleto foi
            # pago.
            notify_new_paid_subscription_credit_card(
                event,
                transaction
            )

        elif is_refused:
            notify_new_refused_subscription_credit_card(
                event,
                transaction
            )

        elif is_refunded:
            notify_refunded_subscription_credit_card(
                event,
                transaction
            )

        else:
            msg = 'Notificação de transação de cartão de crédito'
            msg += ' de inscrição não pôde ser realizada devido ao'
            msg += ' seguinte erro: status desconhecido para'
            msg += ' notificação - "{}". Evento: {}. Inscrição: {}'
            msg += ' ({} - {} - {}). Transaction {}.'
            msg += msg.format(
                new_status,
                event.name,
                sub_user.get_full_name(),
                sub_user.pk,
                sub_user.email,
                transaction.subscription.pk,
                transaction.pk,
            )

            raise mailer_notification.NotifcationError(msg)
