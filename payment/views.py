import json
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

from core.helpers import sentry_log as log
from gatheros_event.helpers.account import update_account
from gatheros_event.models import Event
from gatheros_event.views.mixins import AccountMixin
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
from mailer.tasks import send_mail
from payment.forms import PagarMeCheckoutForm, PaymentForm
from payment.helpers import (
    TransactionDirector, \
    TransactionSubscriptionStatusIntegrator,
    TransactionLog,
)
from payment.models import Transaction, TransactionStatus


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


class EventPaymentView(AccountMixin, ListView):
    template_name = 'payments/list.html'
    # template_name = 'maintainance.html'
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
        context['totals'] = self._get_payables()
        context['has_inside_bar'] = True
        context['active'] = 'pagamentos'
        context['has_paid_lots'] = True

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
        log(message=msg, type='warning', notify_admins=True, )
        raise Http404

    transaction_log.add_message('Buscando transação na persistência.', True)
    transaction = Transaction.objects.get(uuid=uidb64)
    transaction_log.add_message('Transação encontrada.')

    data = request.data.copy()

    if not data:
        msg = 'Houve uma tentativa de postback sem dados de transação para a' \
              ' transação "{}"'.format(uidb64)

        transaction_log.add_message(msg, save=True)

        log(message=msg, type='warning', notify_admins=True, extra_data={
            'uuid': uidb64,
            'transaction': transaction.pk,
            'send_data': data,
        })
        return HttpResponseBadRequest()

    transaction_log.add_message(
        "Dados da transação recebidos: \n----- \n{} \n-----".format(
            json.dumps(data)
        )
    )
    subscription = transaction.subscription
    transaction_log.add_message('ID da Inscrição: {}.'.format(subscription.pk))

    previous_status = transaction.status
    incoming_status = data.get('current_status', '')

    transaction_log.add_message('Status anterior: {}.'.format(previous_status))
    transaction_log.add_message('Status a ser registrado: {}.'.format(
        incoming_status
    ))

    # Se não irá mudar o status de transação, não há o que processar.
    if previous_status == incoming_status:
        transaction_log.add_message(
            'Nada a ser feito: o status não mudou',
            save=True
        )
        # @TODO - caso algum erro aconteça no lado da Congressy, coloca
        # a transação paga em uma fila para ser reprocessada novamente
        # em caso de ser o mesmo status mas não houve registro correto
        # de notificação ou criação de pagamento.
        return Response(status=200)

    transaction.status = incoming_status

    transaction_log.add_message('Tipo de transação: {}.'.format(
        transaction.type
    ))

    if transaction.type == Transaction.BOLETO:
        boleto_url = data.get('transaction[boleto_url]')
        transaction.data['boleto_url'] = boleto_url
        transaction.boleto_url = boleto_url

    # ============================== PAYMENT ============================ #
    with atomic():
        transaction_log.add_message('Iniciando processamento atômico.', True)

        # Create a state machine using the old transaction status as it's
        # initial value.
        transaction_director = TransactionDirector(
            status=incoming_status,
            old_status=previous_status,
        )
        transaction_director_status = transaction_director.direct()
        transaction_log.add_message(
            'Validação do Diretor do status da transação: {}'.format(
                transaction_director_status
            ),
            save=True
        )

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

        transaction_log.add_message(
            'Validação do Integrador do status de inscrição a ser'
            ' registrado de acordo com status de transação:'
            ' {}'.format(subscription_status),
            save=True
        )
        transaction.subscription.save()

        transaction_log.add_message(
            'Preparando para atualizar inscrição - status: {}'.format(
                subscription_status
            ),
            True
        )

        # Persists transaction change
        transaction.save()
        transaction_log.add_message('Transação atualizada.')

        if incoming_status == Transaction.PAID:
            transaction_log.add_message(
                'Iniciando registro de pagamento.',
                save=True
            )

            try:
                transaction.payment.paid = True
                transaction.payment.save()
                transaction_log.add_message(
                    'Pagamento atualizado - status: pago.'
                )

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

                    transaction_log.add_message(msg, save=True)

                    raise Exception(msg)

                # por agora, não vamos vincular pagamento a nada.
                payment_form.save()
                transaction_log.add_message('Novo Pagamento registrado.')

        transaction_log.add_message('Preparando registro de status.', True)

        # Registra status de transação.
        TransactionStatus.objects.create(
            transaction=transaction,
            data=data,
            date_created=datetime.now().strftime(
                "%Y-%m-%dT%H:%M:%S.%fZ"
            ),
            status=incoming_status,
        )
        transaction_log.add_message('Status criado com sucesso.')

        subscription = transaction.subscription
        event = subscription.event

        sub_user = subscription.person.user

        is_new_subscription = subscription.notified is False
        is_paid = incoming_status == Transaction.PAID
        is_refused = incoming_status == Transaction.REFUSED
        is_refunded = incoming_status == Transaction.REFUNDED
        is_waiting = incoming_status == Transaction.WAITING_PAYMENT
        is_pending_refund = incoming_status == Transaction.PENDING_REFUND
        is_chargedback = incoming_status == Transaction.CHARGEDBACK

        transaction_log.add_message(
            'Registro condições de notificação: \n{}'.format(
                "\n".join([
                    '   - Nova Inscrição: {}'.format(is_new_subscription),
                    '   - Pago: {}'.format(is_paid),
                    '   - Recusado: {}'.format(is_refused),
                    '   - Reembolso: {}'.format(is_refunded),
                    '   - Aguardando: {}'.format(is_waiting),
                    '   - Pendente para reembolso: {}'.format(
                        is_pending_refund),
                    '   - Chargedback: {}'.format(is_chargedback),
                ])
            )
        )

        try:
            if is_new_subscription is True:
                transaction_log.add_message(
                    'Processando notificação como nova inscrição:'
                    ' {}'.format(transaction.type),
                    save=True
                )

                if transaction.type == Transaction.BOLETO:

                    if is_waiting:
                        # Novas inscrições nunca estão pagas.
                        notify_new_user_and_unpaid_subscription_boleto(
                            event,
                            transaction
                        )
                        transaction_log.add_message('Enviado por {}'.format(
                            'notify_new_user_and_unpaid_subscription_boleto'
                        ))

                    elif is_paid:
                        # Se não é status inicial, certamente o boleto foi]
                        # pago.
                        notify_new_user_and_paid_subscription_boleto(
                            event,
                            transaction
                        )
                        transaction_log.add_message('Enviado por {}'.format(
                            'notify_new_user_and_paid_subscription_boleto'
                        ))

                    elif is_refused:
                        # Quando a emissão do boleto falha por algum motivo.
                        notify_new_user_and_refused_subscription_boleto(
                            event,
                            transaction
                        )
                        transaction_log.add_message('Enviado por {}'.format(
                            'notify_new_user_and_refused_subscription_boleto'
                        ))

                    elif is_refunded:
                        notify_refunded_subscription_boleto(event, transaction)
                        transaction_log.add_message('Enviado por {}'.format(
                            'notify_refunded_subscription_boleto'
                        ))

                    elif is_chargedback:
                        notify_chargedback_subscription(event, transaction)
                        transaction_log.add_message('Enviado por {}'.format(
                            'notify_chargedback_subscription'
                        ))

                    else:
                        msg = 'Notificação de transação de boleto de nova' \
                              ' inscrição não pôde ser realizada devido ao' \
                              ' seguinte erro: status desconhecido para' \
                              ' notificação - "{}". Evento: {}. Inscrição:' \
                              ' {} ({} - {} - {}). Transaction {}.'.format(
                            incoming_status,
                            event.name,
                            sub_user.get_full_name(),
                            sub_user.pk,
                            sub_user.email,
                            transaction.subscription.pk,
                            transaction.pk,
                        )

                        transaction_log.add_message(msg, save=True)

                        raise mailer_notification.NotifcationError(msg)

                elif transaction.type == Transaction.CREDIT_CARD:

                    if is_waiting:
                        # Pode acontecer um delay no pagamento de cartão
                        notify_new_user_and_unpaid_subscription_credit_card(
                            event,
                            transaction
                        )
                        transaction_log.add_message('Enviado por {}'.format(
                            'notify_new_user_and_unpaid_subscription_credit'
                            '_card'
                        ))

                    elif is_paid:
                        # Se não é status inicial, certamente o boleto foi
                        # pago.
                        notify_new_user_and_paid_subscription_credit_card(
                            event,
                            transaction
                        )
                        transaction_log.add_message('Enviado por {}'.format(
                            'notify_new_user_and_paid_subscription_credit_card'
                        ))

                    elif is_refused:
                        notify_new_user_and_refused_subscription_credit_card(
                            event,
                            transaction
                        )
                        transaction_log.add_message(
                            'Enviado por {}'.format(
                                'notify_new_user_and_refused_subscription_'
                                'credit_card'
                            )
                        )

                    elif is_refunded:
                        notify_refunded_subscription_credit_card(
                            event,
                            transaction
                        )
                        transaction_log.add_message('Enviado por {}'.format(
                            'notify_refunded_subscription_credit_card'
                        ))

                    elif is_chargedback:
                        notify_chargedback_subscription(event, transaction)
                        transaction_log.add_message('Enviado por {}'.format(
                            'notify_chargedback_subscription'
                        ))

                    else:

                        msg = 'Notificação de transação de cartão de crédito'
                        msg += ' de nova inscrição não pôde ser realizada'
                        msg += ' devido ao seguinte erro: status desconhecido'
                        msg += ' para notificação - "{}". Evento: {}.'
                        msg += ' Inscrição: {} ({} - {} - {}).'
                        msg += ' Transaction {}.'
                        msg += msg.format(
                            incoming_status,
                            event.name,
                            sub_user.get_full_name(),
                            sub_user.pk,
                            sub_user.email,
                            transaction.subscription.pk,
                            transaction.pk,
                        )

                        transaction_log.add_message(msg, save=True)

                        raise mailer_notification.NotifcationError(msg)

                else:
                    msg = 'Notificação de transação de nova inscrição não'
                    msg += ' pôde ser realizada devido ao seguinte erro:'
                    msg += ' método de pagamento desconhecido para'
                    msg += ' notificação - "{}". Evento: {}. Inscrição:'
                    msg += ' {} ({} - {} - {}). Transaction {}. '
                    msg += msg.format(
                        incoming_status,
                        event.name,
                        sub_user.get_full_name(),
                        sub_user.pk,
                        sub_user.email,
                        transaction.subscription.pk,
                        transaction.pk,
                    )

                    transaction_log.add_message(msg, save=True)

                    raise mailer_notification.NotifcationError(msg)

            # Não é nova inscrição
            else:
                transaction_log.add_message(
                    'Processando notificação como atualização de inscrição:'
                    ' {}'.format(transaction.type),
                    save=True
                )

                if transaction.type == Transaction.BOLETO:

                    if is_waiting:
                        notify_new_unpaid_subscription_boleto(
                            event,
                            transaction
                        )
                        transaction_log.add_message('Enviado por {}'.format(
                            'notify_new_unpaid_subscription_boleto'
                        ))

                    # Se não é status inicial, certamente o boleto foi pago.
                    elif is_paid:
                        notify_paid_subscription_boleto(event, transaction)
                        transaction_log.add_message('Enviado por {}'.format(
                            'notify_paid_subscription_boleto'
                        ))

                    elif is_refused:
                        # Possivelmente por alguma falha.
                        notify_new_refused_subscription_boleto(
                            event,
                            transaction
                        )
                        transaction_log.add_message('Enviado por {}'.format(
                            'notify_new_refused_subscription_boleto'
                        ))

                    elif is_refunded:
                        notify_refunded_subscription_boleto(event, transaction)
                        transaction_log.add_message('Enviado por {}'.format(
                            'notify_refunded_subscription_boleto'
                        ))

                    elif is_pending_refund:
                        notify_pending_refund_subscription_boleto(
                            event,
                            transaction
                        )
                        transaction_log.add_message('Enviado por {}'.format(
                            'notify_pending_refund_subscription_boleto'
                        ))

                    else:
                        msg = 'Notificação de transação de boleto de inscrição'
                        msg += ' não pôde ser realizada devido ao seguinte'
                        msg += ' erro: status desconhecido para notificação'
                        msg += '  - "{}".'
                        msg += ' Evento: {}. Inscrição: {} ({} - {} - {}).'
                        msg += ' Transaction {}.'
                        msg += msg.format(
                            incoming_status,
                            event.name,
                            sub_user.get_full_name(),
                            sub_user.pk,
                            sub_user.email,
                            transaction.subscription.pk,
                            transaction.pk,
                        )

                        transaction_log.add_message(msg, save=True)

                        raise mailer_notification.NotifcationError(msg)

                elif transaction.type == Transaction.CREDIT_CARD:

                    if is_waiting:
                        # Pode acontecer um delay no pagamento de cartão
                        notify_new_unpaid_subscription_credit_card(
                            event,
                            transaction
                        )
                        transaction_log.add_message('Enviado por {}'.format(
                            'notify_new_unpaid_subscription_credit_card'
                        ))

                    elif is_paid:
                        # Se não é status inicial, certamente o boleto foi
                        # pago.
                        notify_new_paid_subscription_credit_card(
                            event,
                            transaction
                        )
                        transaction_log.add_message('Enviado por {}'.format(
                            'notify_new_paid_subscription_credit_card'
                        ))

                    elif is_refused:
                        notify_new_refused_subscription_credit_card(
                            event,
                            transaction
                        )
                        transaction_log.add_message('Enviado por {}'.format(
                            'notify_new_refused_subscription_credit_card'
                        ))

                    elif is_refunded:
                        notify_refunded_subscription_credit_card(
                            event,
                            transaction
                        )
                        transaction_log.add_message('Enviado por {}'.format(
                            'notify_refunded_subscription_credit_card'
                        ))

                    else:
                        msg = 'Notificação de transação de cartão de crédito'
                        msg += ' de inscrição não pôde ser realizada devido ao'
                        msg += ' seguinte erro: status desconhecido para'
                        msg += ' notificação - "{}". Evento: {}. Inscrição: {}'
                        msg += ' ({} - {} - {}). Transaction {}.'
                        msg += msg.format(
                            incoming_status,
                            event.name,
                            sub_user.get_full_name(),
                            sub_user.pk,
                            sub_user.email,
                            transaction.subscription.pk,
                            transaction.pk,
                        )

                        transaction_log.add_message(msg, save=True)

                        raise mailer_notification.NotifcationError(msg)

                else:
                    msg = 'Notificação de transação de inscrição não pôde ser'
                    msg += ' realizada devido ao seguinte erro: método de'
                    msg += ' pagamento desconhecido para notificação - "{}".'
                    msg += ' Evento: {}. Inscrição: {} ({} - {} - {}).'
                    msg += ' Transaction {}.'.format(
                        incoming_status,
                        event.name,
                        sub_user.get_full_name(),
                        sub_user.pk,
                        sub_user.email,
                        transaction.subscription.pk,
                        transaction.pk,
                    )

                    transaction_log.add_message(msg, save=True)

                    raise mailer_notification.NotifcationError(msg)

        except mailer_notification.NotifcationError as e:
            transaction_log.add_message(str(e), save=True)
            raise e

        transaction_log.add_message('Notificação realizada com sucesso')

        # Registra inscrição como notificada.
        transaction_log.add_message('Registrando inscrição como notificada.')
        transaction.subscription.notified = True
        transaction.subscription.save()
        transaction_log.add_message('Inscrição registrada como notificada.')

        try:
            transaction_log.add_message(
                'Preparando notificação de postback para admins.',
                save=True
            )
            notify_postback(transaction, data)
            transaction_log.add_message(
                'Postback para admins realizado com sucesso.'
            )

        except Exception as e:
            msg = 'Erro na notificação para administradores sobre novo' \
                  ' postback. Tudo funcionou bem, menos a notificação. O' \
                  ' provedor foi notificado como tudo certo e não' \
                  ' tentará novamente. Erro(s): {}'.format(e)

            transaction_log.add_message(msg)

            log(
                message=msg,
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

        transaction_log.add_message('Fim de processamento.', save=True)

        return Response(status=201)
