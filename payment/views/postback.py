from datetime import datetime
from decimal import Decimal

from django.db.models import Sum
from django.db.transaction import atomic
from django.http import (
    Http404,
    HttpResponseBadRequest,
)
from rest_framework.decorators import api_view
from rest_framework.response import Response

from core.helpers import sentry_log
from payment.email_notifications import PaymentNotification
from payment.forms import PaymentForm
from payment.helpers import (
    TransactionLog,
)
from payment.models import Transaction, TransactionStatus
from payment.postback import Postback
from payment.subscription_status_manager import SubscriptionStatusManager
from .helpers import notify_admins_postback


@api_view(['POST'])
def postback_url_view(request, uidb64):
    transaction_log = TransactionLog(uidb64)

    if not uidb64:
        msg = 'Houve uma tentativa de postback sem identificador do postback.'
        transaction_log.add_message(msg, save=True)
        sentry_log(message=msg, type='warning', notify_admins=True, )
        raise Http404

    transaction_log.add_message('Buscando transação na persistência.', True)
    transaction = Transaction.objects.get(uuid=uidb64)
    transaction_log.add_message('Transação encontrada.')

    data = request.data.copy()

    if not data:
        msg = 'Houve uma tentativa de postback sem dados de transação para a' \
              ' transação "{}"'.format(uidb64)

        transaction_log.add_message(msg, save=True)

        sentry_log(message=msg, type='warning', notify_admins=True, extra_data={
            'uuid': uidb64,
            'transaction': transaction.pk,
            'send_data': data,
        })
        return HttpResponseBadRequest()

    post_back = Postback(
        transaction_pk=str(transaction.pk),
        transaction_amount=transaction.amount,
        transaction_status=transaction.status,
        transaction_type=transaction.type,
    )

    with atomic():

        # ================= TRANSACTION ====================================
        transaction.status = post_back.get_new_status(payload=data)

        # Alterando a URL de boleto
        if transaction.type == Transaction.BOLETO:
            boleto_url = data.get('transaction[boleto_url]')
            transaction.data['boleto_url'] = boleto_url
            transaction.boleto_url = boleto_url

        transaction.save()

        # ==================================================================

        # ================= SUBSCRIPTION ===================================

        subscription = transaction.subscription
        subscription_status_manager = SubscriptionStatusManager(
            subscription_status=subscription.status,
            transaction_pk=str(transaction.pk),
            transaction_status=transaction.status,
            transaction_value=transaction.amount,
        )

        debt = Decimal(0)
        existing_amount = Decimal(0)

        if transaction.amount > Decimal(0):

            # Pegar o valor da divida
            debts = subscription.debts.all()
            for debt in debts:
                debt += debt.amount

            # Pegar qualquer dinheiro já pago
            existing_amount = subscription.payments.filter(
                paid=True
            ).aggregate(total=Sum('amount'))

            existing_amount = existing_amount['total']

        subscription.status = subscription_status_manager.get_new_status(
            debt=debt,
            existing_payments=existing_amount,
        )

        subscription.save()

        # ==================================================================

        # ================= TRANSACTION STATUS =============================

        # Registra status de transação.
        TransactionStatus.objects.create(
            transaction=transaction,
            data=data,
            date_created=datetime.now().strftime(
                "%Y-%m-%dT%H:%M:%S.%fZ"
            ),
            status=data.get('current_status'),
        )

        # ==================================================================

        # ================= PAYMENT ========================================

        if data.get('current_status') == Transaction.PAID:

            try:
                transaction.payment.paid = True
                transaction.payment.save()

            except AttributeError:
                payment_form = PaymentForm(
                    subscription=subscription,
                    transaction=transaction,
                    data={
                        'cash_type': transaction.type,
                        'amount': transaction.amount,
                    },
                )

                if not payment_form.is_valid():
                    error_msgs = []
                    for field, errs in payment_form.errors.items():
                        error_msgs.append(str(errs))

                    msg = 'Erro ao criar pagamento de uma transação:' \
                          ' {}'.format("".join(error_msgs))

                    raise Exception(msg)

                # por agora, não vamos vincular pagamento a nada.
                payment_form.save()

        # ==================================================================

        # ================= NOTIFICATION ===================================

        notification = PaymentNotification(
            transaction=transaction,
        )

        notification.notify()

        # Registra inscrição como notificada.
        subscription.notified = True
        subscription.save()

        notify_admins_postback(transaction, data)

        return Response(status=201)
