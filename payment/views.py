import json
from decimal import Decimal
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic import ListView
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view
from rest_framework.response import Response

from gatheros_event.helpers.account import update_account
from gatheros_event.models import Event
from gatheros_subscription.models import Subscription
from mailer.tasks import send_mail
from payment.models import Transaction, TransactionStatus
from payment.helpers import TransactionDirector, \
    TransactionSubscriptionStatusIntegrator


class EventPaymentView(LoginRequiredMixin, ListView):
    template_name = 'payments/list.html'
    event = None

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

        old_status = transaction.status

        data = request.data.copy()

        transaction_status = TransactionStatus(
            transaction=transaction,
            data=data
        )

        status = data.get('current_status', '')

        transaction.status = status
        transaction.data['boleto_url'] = data.get(
            'transaction[boleto_url]',
            ''
        )
        transaction.save()

        transaction_status.data['status'] = status
        transaction_status.date_created = data.get('transaction[date_created]')
        transaction_status.status = status
        transaction_status.save()

        subscription = Subscription.objects.get(pk=transaction.subscription.pk)

        # Create a state machine using the old transaction status as it's
        # initial value.

        transaction_director = TransactionDirector(status=status,
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

    except ObjectDoesNotExist:
        raise Http404

    return Response(status=201)
