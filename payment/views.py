import json
import logging
from datetime import datetime
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

from gatheros_event.helpers.account import update_account
from gatheros_event.helpers.event_business import is_paid_event
from gatheros_event.models import Event
from gatheros_event.views.mixins import AccountMixin, EventDraftStateMixin
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
    notify_refunded_subscription_credit_card,
)
from mailer.tasks import send_mail
from payment.forms import PagarMeCheckoutForm, PaymentForm
from payment.helpers import (
    TransactionDirector,
    TransactionSubscriptionStatusIntegrator,
)
from payment.models import Transaction, TransactionStatus


try:
    from raven.contrib.django.raven_compat.models import client

    SENTRY_RAVEN = True

except ImportError:
    SENTRY_RAVEN = False


def log(message, extra_data=None, type='error', notify_admins=False):
    logger = logging.getLogger(__name__)

    if type == 'error':
        logger.error(message, extra=extra_data)
        if SENTRY_RAVEN:
            client.captureMessage(message, **extra_data)

    if type == 'warning':
        logger.warning(message, extra=extra_data)

        if notify_admins is True and SENTRY_RAVEN:
            client.captureMessage(message, **extra_data)

    if type == 'message':
        logger.info(message, extra=extra_data)

        if notify_admins is True and SENTRY_RAVEN:
            client.captureMessage(message)


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
        kwargs.update({'event': self.event})
        context.update(EventDraftStateMixin.get_context_data(self, **kwargs))
        context['event'] = self.event
        context['totals'] = self._get_payables()
        context['has_inside_bar'] = True
        context['active'] = 'pagamentos'
        context['is_paid_event'] = is_paid_event(self.event)

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
    if not uidb64:
        log(
            message='Houve uma tentativa de postback sem identificador do'
                    ' postback.',
            type='warning',
            notify_admins=True,
        )
        raise Http404

    transaction = Transaction.objects.get(uuid=uidb64)

    data = request.data.copy()
    subscription = transaction.subscription

    if not data:
        log(
            message='Houve uma tentativa de postback sem dados de'
                    ' transação para a transação "{}"'.format(uidb64),
            type='warning',
            extra_data={
                'uuid': uidb64,
                'transaction': transaction.pk,
                'send_data': data,
            },
            notify_admins=True,
        )
        return HttpResponseBadRequest()

    previous_status = transaction.status
    incoming_status = data.get('current_status', '')

    # Se não irá mudar o status de transação, não há o que processar.
    if previous_status == incoming_status:
        # @TODO - caso algum erro aconteça no lado da Congressy, coloca
        # a transação paga em uma fila para ser reprocessada novamente
        # em caso de ser o mesmo status mas não houve registro correto
        # de notificação ou criação de pagamento.
        return Response(status=200)

    transaction.status = incoming_status

    if transaction.type == Transaction.BOLETO:
        boleto_url = data.get('transaction[boleto_url]')
        transaction.data['boleto_url'] = boleto_url
        transaction.boleto_url = boleto_url

    # ============================== PAYMENT ============================ #
    with atomic():
        # Create a state machine using the old transaction status as it's
        # initial value.
        transaction_director = TransactionDirector(
            status=incoming_status,
            old_status=previous_status,
        )
        transaction_director_status = transaction_director.direct()

        # Translate/integrate the status returned from the director to a
        #   subscription status.
        trans_sub_status_integrator = \
            TransactionSubscriptionStatusIntegrator(
                transaction_director_status
            )

        # Atualiza o objeto de subscription a partir de transaction
        # para que os dados e inscrições sejam resgatados a partir
        # de transaction sem resgatar os dados da peristência
        # novamente.
        subscription_status = trans_sub_status_integrator.integrate()
        transaction.subscription.status = subscription_status
        transaction.subscription.completed = True
        transaction.subscription.save()

        # Persists transaction change
        transaction.save()

        if incoming_status == Transaction.PAID:

            try:
                payment = transaction.payment
                transaction.type = transaction.type
                transaction.amount = transaction.amount
                payment.paid = True
                payment.save()

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

                    raise Exception(
                        'Erro ao criar pagamento de uma transação: {}'.format(
                            "".join(error_msgs)
                        )
                    )

                # por agora, não vamos vincular pagamento a nada.
                payment_form.save()

        # Registra status de transação.
        TransactionStatus.objects.create(
            transaction=transaction,
            data=data,
            date_created=datetime.now().strftime(
                "%Y-%m-%dT%H:%M:%S.%fZ"
            ),
            status=incoming_status,
        )

        subscription = transaction.subscription
        event = subscription.event

        sub_user = subscription.person.user

        is_new_subscription = subscription.notified is False
        is_paid = incoming_status == Transaction.PAID
        is_refused = incoming_status == Transaction.REFUSED
        is_refunded = incoming_status == Transaction.REFUNDED
        is_waiting = incoming_status == Transaction.WAITING_PAYMENT
        is_chargedback = incoming_status == Transaction.CHARGEDBACK

        try:
            if is_new_subscription is True:
                if transaction.type == Transaction.BOLETO:

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
                        notify_refunded_subscription_boleto(event, transaction)

                    elif is_chargedback:
                        notify_chargedback_subscription(event, transaction)

                    else:
                        raise mailer_notification.NotifcationError(
                            'Notificação de transação de boleto de nova'
                            ' inscrição não pôde ser realizada devido ao'
                            ' seguinte erro: status desconhecido para'
                            ' notificação - "{}". Evento: {}. Inscrição:'
                            ' {} ({} - {} - {}). Transaction {}: '.format(
                                incoming_status,
                                event.name,
                                sub_user.get_full_name(),
                                sub_user.pk,
                                sub_user.email,
                                transaction.subscription.pk,
                                transaction.pk,
                            )
                        )

                elif transaction.type == Transaction.CREDIT_CARD:

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
                        raise mailer_notification.NotifcationError(
                            'Notificação de transação de cartão de crédito de'
                            ' nova inscrição não pôde ser realizada devido ao'
                            ' seguinte erro: status desconhecido para'
                            ' notificação - "{}". Evento: {}. Inscrição: {}'
                            ' ({} - {} - {}). Transaction {}: '.format(
                                incoming_status,
                                event.name,
                                sub_user.get_full_name(),
                                sub_user.pk,
                                sub_user.email,
                                transaction.subscription.pk,
                                transaction.pk,
                            )
                        )

                else:
                    raise mailer_notification.NotifcationError(
                        'Notificação de transação de nova inscrição não pôde'
                        ' ser realizada devido ao seguinte erro: método de'
                        ' pagamento desconhecido para notificação - "{}".'
                        ' Evento: {}. Inscrição: {} ({} - {} - {}).'
                        ' Transaction {}: '.format(
                            incoming_status,
                            event.name,
                            sub_user.get_full_name(),
                            sub_user.pk,
                            sub_user.email,
                            transaction.subscription.pk,
                            transaction.pk,
                        )
                    )

            # Não é nova inscrição
            else:
                if transaction.type == Transaction.BOLETO:

                    if is_waiting:
                        notify_new_unpaid_subscription_boleto(
                            event,
                            transaction)

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
                        notify_refunded_subscription_boleto(event, transaction)

                    else:
                        raise mailer_notification.NotifcationError(
                            'Notificação de transação de boleto de inscrição'
                            ' não pôde ser realizada devido ao seguinte erro:'
                            ' status desconhecido para notificação - "{}".'
                            ' Evento: {}. Inscrição: {} ({} - {} - {}).'
                            ' Transaction {}: '.format(
                                incoming_status,
                                event.name,
                                sub_user.get_full_name(),
                                sub_user.pk,
                                sub_user.email,
                                transaction.subscription.pk,
                                transaction.pk,
                            )
                        )

                elif transaction.type == Transaction.CREDIT_CARD:

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
                        raise mailer_notification.NotifcationError(
                            'Notificação de transação de cartão de crédito de'
                            ' inscrição não pôde ser realizada devido ao'
                            ' seguinte erro: status desconhecido para'
                            ' notificação - "{}". Evento: {}. Inscrição: {}'
                            ' ({} - {} - {}). Transaction {}: '.format(
                                incoming_status,
                                event.name,
                                sub_user.get_full_name(),
                                sub_user.pk,
                                sub_user.email,
                                transaction.subscription.pk,
                                transaction.pk,
                            )
                        )

                else:
                    raise mailer_notification.NotifcationError(
                        'Notificação de transação de inscrição não pôde ser'
                        ' realizada devido ao seguinte erro: método de'
                        ' pagamento desconhecido para notificação - "{}".'
                        ' Evento: {}. Inscrição: {} ({} - {} - {}).'
                        ' Transaction {}: '.format(
                            incoming_status,
                            event.name,
                            sub_user.get_full_name(),
                            sub_user.pk,
                            sub_user.email,
                            transaction.subscription.pk,
                            transaction.pk,
                        )
                    )

        except mailer_notification.NotifcationError as e:
            raise e

        # Registra inscrição como notificada.
        transaction.subscription.notified = True
        transaction.subscription.save()

    try:
        notify_postback(transaction, data)

    except Exception as e:
        log(
            message='Erro na notificação para administradores sobre novo'
                    ' postback. Tudo funcionou bem, menos a notificação. O'
                    ' provedor foi notificado como tudo certo e não tentará'
                    ' novamente. Erro(s): {}'.format(e),
            type='error',
            extra_data={
                'uuid': uidb64,
                'transaction': transaction.pk,
                'transaction_status': previous_status,
                'incoming_status': incoming_status,
                'send_data': data,
            },
            notify_admins=True,
        )

    return Response(status=201)
