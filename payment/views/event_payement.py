import locale
from collections import OrderedDict
from decimal import Decimal

from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.formats import localize
from django.views.generic.base import TemplateView

from gatheros_event.helpers.account import update_account
from gatheros_event.helpers.event_business import is_paid_event
from gatheros_event.models import Event
from gatheros_event.views.mixins import AccountMixin, EventDraftStateMixin
from installment.models import Contract
from payment.models import Transaction


class EventPaymentView(AccountMixin, TemplateView, EventDraftStateMixin):
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

        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

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
        context['subscriptions'] = self.get_subscriptions()
        context['is_paid_event'] = is_paid_event(self.event)

        context.update(self.get_event_state_context_data(self.event))

        return context

    def get_subscriptions(self):

        all_transactions = Transaction.objects.filter(
            subscription__event_id=self.event.pk
        ).exclude(
            status__in=[
                Transaction.REFUNDED,
                Transaction.PROCESSING,
                Transaction.PENDING_REFUND,
                Transaction.CHARGEDBACK,
            ]
        ).order_by(Lower('subscription__person__name'),)[:10]

        queryset = all_transactions

        subscriptions = OrderedDict()

        a = Decimal(0)

        for transaction in queryset.all():
            if transaction.status == Transaction.WAITING_PAYMENT \
                    and transaction.manual:
                continue

            sub_pk = str(transaction.subscription_id)

            if sub_pk not in subscriptions:
                sub = transaction.subscription
                subscriptions[sub_pk] = OrderedDict()
                subscriptions[sub_pk]['pk'] = sub.pk
                subscriptions[sub_pk]['lot_name'] = sub.lot.name
                subscriptions[sub_pk]['name'] = sub.person.name.upper()
                subscriptions[sub_pk]['transactions'] = list()

            subscriptions[sub_pk]['transactions'].append({
                'is_boleto': transaction.type == Transaction.BOLETO,
                'is_cc': transaction.type == Transaction.CREDIT_CARD,
                'is_manual': transaction.type == Transaction.MANUAL,
                'type_name': transaction.get_type_display(),
                'is_paid': transaction.paid is True,
                'is_refused': transaction.status == Transaction.REFUSED,
                'is_part': transaction.part_id is not None,
                'is_pending':
                    transaction.status == Transaction.WAITING_PAYMENT,
                'status_name': transaction.get_status_display(),
                'liquid_amount': localize(transaction.liquid_amount),
            })

            if transaction.status == Transaction.WAITING_PAYMENT:
                a += transaction.liquid_amount

        contracts = Contract.objects.filter(
            status__in=[Contract.OPEN_STATUS, Contract.FULLY_PAID_STATUS],
            subscription__event_id=self.event.pk,
        ).order_by(Lower('subscription__person__name'),)[:10]

        for contract in contracts:
            sub_pk = str(contract.subscription_id)

            if sub_pk not in subscriptions:
                sub = contract.subscription
                subscriptions[sub_pk] = OrderedDict()
                subscriptions[sub_pk]['pk'] = sub.pk
                subscriptions[sub_pk]['lot_name'] = sub.lot.name
                subscriptions[sub_pk]['name'] = sub.person.name.upper()
                subscriptions[sub_pk]['transactions'] = list()

            for part in contract.parts.filter(paid=False):
                subscriptions[sub_pk]['transactions'].append({
                    'is_boleto': False,
                    'is_cc': False,
                    'is_manual': True,
                    'type_name': 'Manual',
                    'is_paid': part.paid is True,
                    'is_refused': False,
                    'is_pending': part.paid is False,
                    'is_part': True,
                    'status_name': 'Pago' if part.paid else 'Pendente',
                    'liquid_amount': localize(part.amount),
                })

                if part.paid is False:
                    a += part.amount

        # Vamos considerar apenas pagamentos finais:
        # Se paga, ignorar outras; ou
        # Se recusado, ignorar outras; ou
        # Se pendente, exibir

        for _, sub in subscriptions.items():
            paid_transactions = list()
            refused_transactions = list()
            pending_transactions = list()

            for trans in sub['transactions']:
                if trans['is_paid']:
                    paid_transactions.append(trans)
                elif trans['is_refused']:
                    refused_transactions.append(trans)
                elif trans['is_pending']:
                    pending_transactions.append(trans)

            if paid_transactions:
                subscriptions[_]['transactions'] = paid_transactions
            elif refused_transactions:
                subscriptions[_]['transactions'] = refused_transactions
            elif pending_transactions:
                subscriptions[_]['transactions'] = pending_transactions

        return subscriptions

    def _get_payables(self):

        totals = {
            'total': Decimal(0.00),
            'pending': Decimal(0.00),
            'paid': Decimal(0.00),
        }

        transactions = Transaction.objects.filter(
            subscription__event_id=self.event.pk,
            status__in=[
                Transaction.PAID,
                Transaction.WAITING_PAYMENT,
            ]
        )

        for transaction in transactions:
            if transaction.status == Transaction.WAITING_PAYMENT \
                    and transaction.manual:
                continue

            totals['total'] += transaction.liquid_amount or Decimal(0.00)

            if transaction.status == Transaction.PAID:
                totals['paid'] += transaction.liquid_amount or Decimal(0.00)

            if transaction.status == Transaction.WAITING_PAYMENT:
                totals['pending'] += transaction.liquid_amount or Decimal(0.00)

        contracts = Contract.objects.filter(
            status__in=[Contract.OPEN_STATUS, Contract.FULLY_PAID_STATUS],
            subscription__event_id=self.event.pk,
        )

        for contract in contracts:
            for part in contract.parts.filter(paid=False):
                totals['total'] += part.amount or Decimal(0.00)

                if part.paid is False:
                    totals['pending'] += part.amount or Decimal(0.00)

        return totals
