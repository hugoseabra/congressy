import json
from datetime import datetime
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import ListView
from rest_framework.decorators import api_view
from rest_framework.response import Response

from gatheros_event.helpers.account import update_account
from gatheros_event.models import Event
from gatheros_event.views.mixins import AccountMixin
from gatheros_subscription.models import Subscription
from mailer.services import (
    notify_new_paid_subscription_credit_card,
    notify_new_unpaid_subscription_boleto,
    notify_new_unpaid_subscription_credit_card,
    notify_new_user_and_paid_subscription_credit_card,
    notify_new_user_and_paid_subscription_boleto,
    notify_new_user_and_unpaid_subscription_credit_card,
    notify_new_user_and_unpaid_subscription_boleto,
    notify_paid_subscription_boleto,
)
from mailer.tasks import send_mail
from payment.helpers import (
    TransactionDirector,
    TransactionSubscriptionStatusIntegrator,
)
from payment.models import Transaction, TransactionStatus


class EventPaymentView(AccountMixin, ListView):
    template_name = 'payments/list.html'
    event = None

    def can_access(self):
        if not self.event:
            return False

        return self.event.organization == self.organization

    def get_permission_denied_url(self):
        return reverse('event:event-list')

    def dispatch(self, request, *args, **kwargs):

        self.event = get_object_or_404(Event, pk=self.kwargs.get('pk'))
        update_account(
            request=self.request,
            organization=self.event.organization,
            force=True
        )

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(EventPaymentView, self).get_context_data(**kwargs)
        context['event'] = self.event
        context['total_paid_payables'] = self._get_payables(
            transaction_type='paid'
        )
        context['total_payables'] = self._get_payables(
            transaction_type='total'
        )

        return context

    def get_queryset(self):
        all_transactions = Transaction.objects.filter(
            subscription__event=self.event
        ).order_by('subscription__person__name')

        return all_transactions

    def _get_payables(self, transaction_type=None):

        if not transaction_type:
            return 0

        all_transactions = []

        if transaction_type == 'paid':
            all_transactions = Transaction.objects.filter(
                subscription__event=self.event,
                status=Transaction.PAID
            )
        elif transaction_type == 'total':
            all_transactions = Transaction.objects.filter(
                subscription__event=self.event
            )

        total = 0

        congressy_percent = Decimal(settings.CONGRESSY_PLAN_PERCENT_10)
        for transaction in all_transactions:

            if transaction.status == transaction.REFUNDED or \
                            transaction.status == transaction.REFUSED:
                continue

            amount = transaction.amount
            deductible = (congressy_percent * amount) / 100
            calculated_total = transaction.amount - deductible
            total += calculated_total

        return total


@api_view(['POST'])
def postback_url_view(request, uidb64):
    body = """
            We have received a postback call, here is the data:

            <pre><code>{0}</code></pre>
    """.format(json.dumps(request.data))

    send_mail(
        subject="Recived a postbackcall",
        body=body,
        to=settings.DEV_ALERT_EMAILS
    )

    if not uidb64:
        raise Http404

    try:
        transaction = Transaction.objects.get(uuid=uidb64)
        subscription = transaction.subscription
        event = subscription.event

        old_status = transaction.status

        data = request.data.copy()

        new_desired_status = data.get('current_status', '')

        # Only continue the postback workflow if the new_desired_status and
        # old_stats are different.
        if old_status == new_desired_status:
            return Response(status=200)

        boleto_url = data.get('transaction[boleto_url]', '')

        transaction_status = TransactionStatus(
            transaction=transaction,
            data=data
        )

        transaction.status = new_desired_status
        transaction.data['boleto_url'] = boleto_url
        transaction.boleto_url = boleto_url
        transaction.save()

        transaction_status.data['status'] = new_desired_status
        transaction_status.date_created = datetime.now().strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        )
        transaction_status.status = new_desired_status
        transaction_status.save()

        subscription = \
            Subscription.objects.get(pk=transaction.subscription.pk)

        # Create a state machine using the old transaction status as it's
        # initial value.

        transaction_director = TransactionDirector(
            status=new_desired_status,
            old_status=old_status)
        transaction_director_status = transaction_director.direct()

        # Translate/integrate the status returned from the director to a
        #   subscription status.
        trans_sub_status_integrator = TransactionSubscriptionStatusIntegrator(
            transaction_director_status)

        subscription_status = trans_sub_status_integrator.integrate()

        if subscription_status:
            subscription.status = subscription_status

        subscription.save()

        payment_method = data.get('transaction[payment_method]')

        sub_user = subscription.person.user
        is_new_subscription = not sub_user.last_login
        is_paid = new_desired_status == Transaction.PAID
        is_starting_status = new_desired_status == Transaction.PROCESSING

        if is_new_subscription:
            if payment_method == Transaction.BOLETO:
                if is_starting_status:
                    # Novas inscrições nunca estão pagas.
                    notify_new_user_and_unpaid_subscription_boleto(
                        event,
                        transaction
                    )

                # Se não é status inicial, certamente o boleto foi pago.
                elif is_paid:
                    notify_new_user_and_paid_subscription_boleto(
                        event,
                        transaction
                    )

            if payment_method == Transaction.CREDIT_CARD:
                if is_starting_status:
                    # Pode acontecer um delay no pagamento de cartão
                    notify_new_user_and_unpaid_subscription_credit_card(
                        event,
                        transaction
                    )

                # Se não é status inicial, certamente o boleto foi pago.
                elif is_paid:
                    notify_new_user_and_paid_subscription_credit_card(
                        event,
                        transaction
                    )

        # Não é nova inscrição
        else:
            if payment_method == Transaction.BOLETO:
                if is_starting_status:
                    notify_new_unpaid_subscription_boleto(event, transaction)

                # Se não é status inicial, certamente o boleto foi pago.
                elif is_paid:
                    notify_paid_subscription_boleto(event, transaction)

            if payment_method == Transaction.CREDIT_CARD:
                if is_starting_status:
                    # Pode acontecer um delay no pagamento de cartão
                    notify_new_unpaid_subscription_credit_card(
                        event,
                        transaction
                    )

                # Se não é status inicial, certamente o boleto foi pago.
                elif is_paid:
                    notify_new_paid_subscription_credit_card(
                        event,
                        transaction
                    )

        return Response(status=201)

    except ObjectDoesNotExist:
        raise Http404
