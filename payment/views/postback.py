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

from buzzlead.services import confirm_bonus
from core.helpers import sentry_log
from payment.email_notifications import PaymentNotification
from payment.forms import PaymentForm
from payment.models import Transaction, TransactionStatus
from payment.payable.updater import update_payables
from payment.postback import Postback
from payment.subscription_status_manager import SubscriptionStatusManager
from payment.transaction_status_collection import TransactionStatusCollection
from .helpers import notify_admins_postback


@api_view(['POST'])
def postback_url_view(request, uidb64):

    if not uidb64:
        msg = 'Houve uma tentativa de postback sem identificador do postback.'
        sentry_log(message=msg, type='warning', notify_admins=True, )
        raise Http404

    transaction = Transaction.objects.get(uuid=uidb64)

    data = request.data.copy()

    if not data:
        msg = 'Houve uma tentativa de postback sem dados de transação para a' \
              ' transação "{}"'.format(uidb64)

        sentry_log(
            message=msg,
            type='warning',
            notify_admins=True,
            extra_data={
                'uuid': uidb64,
                'transaction': transaction.pk,
                'send_data': data,
            }
        )
        return HttpResponseBadRequest()

    # status history
    history = TransactionStatusCollection()
    for status in transaction.statuses.all().order_by('pk'):
        created = datetime.strptime(
            status.date_created,
            "%Y-%m-%dT%H:%M:%S.%fZ"
        )
        history.add(created_on=created, status=status.status, data=status.data)

    post_back = Postback(
        transaction_pk=str(transaction.pk),
        transaction_amount=transaction.amount,
        transaction_status=transaction.status,
        transaction_type=transaction.type,
        transaction_hitsory=history
    )

    with atomic():
        # ================= TRANSACTION ====================================
        new_status = post_back.get_new_status(payload=data)

        if transaction.status == new_status:
            return Response(status=202)

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

        transaction.status = new_status

        # Alterando a URL de boleto
        if transaction.type == Transaction.BOLETO:
            boleto_url = data.get('transaction[boleto_url]')
            transaction.data['boleto_url'] = boleto_url
            transaction.boleto_url = boleto_url

        transaction.save()

        # ===================== PAYABLES ===================================
        for split_rule in transaction.split_rules.all():
            update_payables(split_rule)

        # ================= SUBSCRIPTION ===================================

        subscription = transaction.subscription
        subscription_status_manager = SubscriptionStatusManager(
            subscription_status=subscription.status,
            transaction_pk=str(transaction.pk),
            transaction_status=transaction.status,
            transaction_value=transaction.amount,
        )

        event = subscription.event

        total_debt = Decimal(0)
        existing_amount = Decimal(0)

        if transaction.amount > Decimal(0):

            # Pegar o valor da divida
            debts = subscription.debts.all()
            for debt in debts:
                total_debt += debt.amount

            # Pegar qualquer dinheiro já pago
            existing_amount = subscription.payments.filter(
                paid=True
            ).aggregate(total=Sum('amount'))

            existing_amount = existing_amount['total']

        subscription.status = subscription_status_manager.get_new_status(
            debt=total_debt,
            existing_payments=existing_amount,
        )

        subscription.save()

        # ==================================================================

        # ================= PAYMENT ========================================

        if new_status == Transaction.PAID:

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

            if event.buzzlead_campaigns.count():
                buzzlead_campaign = event.buzzlead_campaigns.first()

                if buzzlead_campaign.enabled is True:
                    confirm_bonus(
                        token=buzzlead_campaign.campaign_owner_token,
                        email_campaign_owner=buzzlead_campaign.signature_email,
                        order_id=buzzlead_campaign.campaign_id,
                    )

        # ==================================================================
        # Registra inscrição como notificada.
        subscription.notified = True
        subscription.save()

        person = subscription.person

        # ================= NOTIFICATION ===================================

        if hasattr(person, 'user') and person.user is not None:
            notification = PaymentNotification(
                transaction=transaction,
            )

            notification.notify()

        notify_admins_postback(transaction, data)

        return Response(status=201)
