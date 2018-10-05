import json
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.db.models import Q
from django.db.transaction import atomic
from django.http import (
    Http404,
    HttpResponseBadRequest,
)
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.formats import localize
from django.views.generic import FormView, ListView
from rest_framework.decorators import api_view
from rest_framework.response import Response

from core.helpers import sentry_log
from gatheros_event.helpers.account import update_account
from gatheros_event.helpers.event_business import is_paid_event
from gatheros_event.models import Event
from gatheros_event.views.mixins import AccountMixin, EventDraftStateMixin
from mailer.tasks import send_mail
from payment.forms import PagarMeCheckoutForm
from payment.helpers import (
    TransactionLog,
)
from payment.models import Transaction
from .postback import Postback, PostbackAmountDiscrepancyError


def notify_postback(transaction, data):
    event = transaction.subscription.event

    body = """
        <br />
        <strong>NOVO POSTBACK:</strong>
        <br /><br />
        <strong>TIPO:</strong> {type_display} ({type})
        <br />
        <strong>Evento:</strong> {event_name} ({event_pk})
        <br />
        <strong>PESSOA:</strong> {person_name}
        <br />
        <strong>E-mail:</strong> {person_email}
        <br />
        <strong>Inscrição:</strong> {sub_pk}
        <br />
        <strong>VALOR (R$):</strong> R$ {amount}
        <br />
        <strong>STATUS:</strong> {status_display} ({status})
        <br />
        <hr >
        <br />
        <strong>Data:</strong>
        <br />    
        <pre><code>{data}</code></pre>
        <br />
    """.format(
        type_display=transaction.get_type_display(),
        type=transaction.type,
        event_name=event.name,
        event_pk=event.pk,
        person_name=transaction.subscription.person.name,
        person_email=transaction.subscription.person.email,
        sub_pk=transaction.subscription.pk,
        amount=localize(transaction.amount),
        status_display=transaction.get_status_display(),
        status=transaction.status,
        data=json.dumps(data),
    )

    send_mail(
        subject="Novo postback: {}".format(event.name),
        body=body,
        to=settings.DEV_ALERT_EMAILS
    )


class EventPaymentView(AccountMixin, ListView, EventDraftStateMixin):
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
        context = super().get_context_data(**kwargs)

        context['event'] = self.event
        context['totals'] = self._get_payables()
        context['has_inside_bar'] = True
        context['active'] = 'pagamentos'
        context['is_paid_event'] = is_paid_event(self.event)

        context.update(self.get_event_state_context_data(self.event))

        return context

    def get_queryset(self):

        all_transactions = Transaction.objects.filter(
            subscription__event=self.event
        ).order_by('subscription__lot__date_start',
                   'subscription__person__name')

        return all_transactions

    def _get_payables(self):

        totals = {
            'total': Decimal(0.00),
            'pending': Decimal(0.00),
            'paid': Decimal(0.00),
        }

        transactions = \
            Transaction.objects.filter(Q(subscription__event=self.event) & (Q(
                status=Transaction.PAID) | Q(
                status=Transaction.WAITING_PAYMENT)))

        for transaction in transactions:
            totals['total'] += transaction.liquid_amount or Decimal(0.00)

            if transaction.paid:
                totals['paid'] += transaction.liquid_amount or Decimal(0.00)

            if transaction.pending:
                totals['pending'] += transaction.liquid_amount or Decimal(0.00)

        return totals


class CheckoutView(AccountMixin, FormView):
    form_class = PagarMeCheckoutForm
    template_name = 'payments/checkout.html'
    success_url = reverse_lazy('public:payment-checkout')
    object = None

    def get_initial(self):
        initial = super().get_initial()
        initial.update(self.request.GET.items())
        return initial

    def get_success_url(self):
        url = self.success_url
        querystrings = []
        for key, value in self.request.GET.items():
            if key == 'csrmiddlewaretoken':
                continue
            querystrings.append('{}={}'.format(key, value))

        return '{}?{}'.format(url, '&'.join(querystrings))

    def post(self, request, *args, **kwargs):
        next_url = self.request.POST.get('next_url')
        if next_url:
            self.success_url = next_url

        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        non_field_errors = form.non_field_errors()
        for error in non_field_errors:
            messages.error(self.request, str(error))

        for hidden_field in form.hidden_fields():
            if hidden_field.errors:
                for error in hidden_field.errors:
                    messages.error(self.request, str(error))

        return super().form_valid(form)


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
        transaction_amount=transaction.amount,
        transaction_status=transaction.status,
        transaction_type=transaction.type,
    )

    with atomic():

        try:

            transaction.status = post_back.get_new_status(payload=data)

            # Alterando a URL de boleto
            if transaction.type == Transaction.BOLETO:
                boleto_url = data.get('transaction[boleto_url]')
                transaction.data['boleto_url'] = boleto_url
                transaction.boleto_url = boleto_url
            transaction.save()

        except PostbackAmountDiscrepancyError as e:

            msg = "Discrepancy in transaction.amount({}) " \
                  "and payload amount({})".format(transaction.amount,
                                                  data.get('amount'))

            sentry_log(
                message=msg,
                type='error',
                extra_data={
                    'transaction': transaction.pk,
                    'transaction_status': transaction.status,
                    'send_data': data,
                },
                notify_admins=True,
            )

            raise e

        return Response(status=201)
