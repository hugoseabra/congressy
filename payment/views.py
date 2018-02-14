import json

from django.conf import settings
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.decorators import api_view
from rest_framework.response import Response

from gatheros_event.models import Event
from mailer.tasks import send_mail
from payment.models import Transaction
from payment.models import TransactionStatus


class EventPaymentView(LoginRequiredMixin, ListView):
    template_name = 'payments/list.html'
    event = None

    def dispatch(self, request, *args, **kwargs):
        self.event = get_object_or_404(Event, pk=self.kwargs.get('pk'))
        response = super().dispatch(request, *args, **kwargs)
        return response

    def get_context_data(self, **kwargs):
        context = super(EventPaymentView, self).get_context_data(**kwargs)
        context['event'] = self.event
        context['total_paid_payables'] = self._get_payables(transaction_type='paid')
        context['total_payables'] = self._get_payables(transaction_type='total')

        return context

    def get_queryset(self):
        all_transactions = Transaction.objects.filter(subscription__event=self.event)

        return all_transactions

    def _get_payables(self, transaction_type=None):

        if not transaction_type:
            return 0

        if transaction_type == 'paid':
            all_transactions = Transaction.objects.filter(subscription__event=self.event, status=Transaction.PAID)
        elif transaction_type == 'total':
            all_transactions = Transaction.objects.filter(subscription__event=self.event)

        total = 0

        for transaction in all_transactions:
            total += transaction.amount

        return total


@api_view(['POST'])
def postback_url_view(request, uidb64):
    body = """
            We have received a postback call, here is the data:
            
            <pre><code>{0}</code></pre>
    """.format(json.dumps(request.data))

    send_mail(subject="Recived a postbackcall", body=body, to=settings.DEV_ALERT_EMAILS)

    if not uidb64:
        raise Http404
    try:
        transaction = Transaction.objects.get(uuid=uidb64)

        data = request.data.copy()

        transaction_status = TransactionStatus(
            transaction=transaction,
            data=data
        )

        status = data.get('current_status', '')

        transaction.data['status'] = status
        transaction.data['boleto_url'] = data.get('transaction[boleto_url]', '')
        transaction.save()

        transaction_status.data['status'] = status
        transaction_status.date_created = data.get('transaction[date_created]')
        transaction_status.status = status
        transaction_status.save()

    except Transaction.DoesNotExist:
        raise Http404

    return Response(status=201)
