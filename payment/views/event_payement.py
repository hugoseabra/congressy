import locale
from collections import OrderedDict
from decimal import Decimal

from django.db.models import Sum, Count, Q
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic.base import TemplateView

from core.views.mixins import TemplateNameableMixin
from gatheros_event.helpers.account import update_account
from gatheros_event.helpers.event_business import is_paid_event
from gatheros_event.models import Event
from gatheros_event.views.mixins import AccountMixin, EventDraftStateMixin
from gatheros_subscription.models import Subscription
from installment.models import Contract
from payment.models import Transaction


class EventPaymentView(AccountMixin,
                       TemplateView,
                       EventDraftStateMixin,
                       TemplateNameableMixin):
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
        context['has_inside_bar'] = True
        context['active'] = 'pagamentos'
        context['is_paid_event'] = is_paid_event(self.event)

        template = self.request.GET.get('template_name')
        if template:
            data_type = 'paid' if template == 'payments/paid' else 'pending'
            context['subscriptions'] = self.get_subscriptions(data_type)
        else:
            context['totals'] = {
                'pending': self._get_pending_total_amount(),
                'paid': 0,
            }


        context.update(self.get_event_state_context_data(self.event))

        return context

    def get_subscriptions(self, data_type):

        sub_filter = self._get_subscriptions_filters(data_type)

        subs = Subscription.objects.filter(**sub_filter)
        subs = subs.order_by(Lower('person__name'))

        trans_filters = self._get_transactions_filters(data_type)

        print(trans_filters)

        subscriptions = OrderedDict()

        a = Decimal(0)

        for sub in subs:

            contracts = sub.installment_contracts.filter(
                status__in=[
                    Contract.OPEN_STATUS,
                    Contract.FULLY_PAID_STATUS,
                ]
            )

            if contracts.count():
                continue

            sub_pk = str(sub.pk)

            transactions_qs = sub.transactions.filter(**trans_filters)

            if sub_pk not in subscriptions:
                subscriptions[sub_pk] = OrderedDict()
                subscriptions[sub_pk]['pk'] = sub.pk
                subscriptions[sub_pk]['lot_name'] = sub.lot.name
                subscriptions[sub_pk]['name'] = sub.person.name.upper()
                subscriptions[sub_pk]['transactions'] = list()

            if transactions_qs.count() == 0:
                if data_type == 'pending':
                    price = sub.lot.get_calculated_price()
                    print('- {} = {} - {}'.format(sub.person.name, price, transactions_qs.count()))
                    subscriptions[sub_pk]['transactions'].append({
                        'is_boleto': False,
                        'is_cc': False,
                        'is_manual': False,
                        'type_name': 'Sem tipo',
                        'is_paid': False,
                        'is_part': False,
                        'is_pending': True,
                        'status_name': 'Aguardando pagamento',
                        'liquid_amount': price,
                    })
                    a += price
                continue

            for trans in transactions_qs:

                subscriptions[sub_pk]['transactions'].append({
                    'is_boleto': trans.type == Transaction.BOLETO,
                    'is_cc': trans.type == Transaction.CREDIT_CARD,
                    'is_manual': trans.type == Transaction.MANUAL,
                    'type_name': trans.get_type_display(),
                    'is_paid': trans.paid is True,
                    'is_part': trans.part_id is not None,
                    'part_info': None,
                    'is_pending': trans.status == Transaction.WAITING_PAYMENT,
                    'status_name': trans.get_status_display(),
                    'liquid_amount': trans.liquid_amount,
                })

                a += trans.liquid_amount

        # contracts = Contract.objects.filter(
        #     status__in=[Contract.OPEN_STATUS, Contract.FULLY_PAID_STATUS],
        #     subscription__event_id=self.event.pk,
        #     parts__paid=data_type == 'paid',
        # ).order_by(
        #     Lower('subscription__person__name'),
        # )
        #
        # for contract in contracts:
        #     sub_pk = str(contract.subscription_id)
        #
        #     if sub_pk not in subscriptions:
        #         sub = contract.subscription
        #         subscriptions[sub_pk] = OrderedDict()
        #         subscriptions[sub_pk]['pk'] = sub.pk
        #         subscriptions[sub_pk]['lot_name'] = sub.lot.name
        #         subscriptions[sub_pk]['name'] = sub.person.name.upper()
        #         subscriptions[sub_pk]['transactions'] = list()
        #
        #     parts_qs = contract.parts
        #
        #     for part in parts_qs.filter(paid=data_type == 'paid').order_by(
        #             'installment_number'
        #     ):
        #         if part.paid and data_type == 'pending':
        #             continue
        #
        #         if part.paid is False and data_type == 'paid':
        #             continue
        #
        #         subscriptions[sub_pk]['transactions'].append({
        #             'is_boleto': False,
        #             'is_cc': False,
        #             'is_manual': True,
        #             'type_name': 'Manual',
        #             'is_paid': part.paid is True,
        #             'is_refused': False,
        #             'is_pending': part.paid is False,
        #             'is_part': True,
        #             'part_info': 'parcela {}/{}'.format(
        #                 part.installment_number,
        #                 contract.num_installments,
        #             ),
        #             'status_name': 'Pago' if part.paid else 'Pendente',
        #             'liquid_amount': part.amount,
        #         })
        #
        #         a += part.amount

        print(a)

        # Vamos considerar apenas pagamentos finais:
        # Se paga, ignorar outras; ou
        # Se recusado, ignorar outras; ou
        # Se pendente, exibir

        sub_names = list()
        for _, sub in subscriptions.items():
            paid_transactions = list()
            pending_transactions = list()

            sub_names.append(sub['name'])

            for trans in sub['transactions']:
                if trans['is_paid']:
                    paid_transactions.append(trans)
                elif trans['is_pending']:
                    pending_transactions.append(trans)

            if paid_transactions:
                subscriptions[_]['transactions'] = paid_transactions
            elif pending_transactions:
                subscriptions[_]['transactions'] = pending_transactions

        sorted_subscriptions = OrderedDict()

        for name in sorted(sub_names):
            for _, sub in subscriptions.items():
                if sub['name'] == name:
                    sorted_subscriptions[_] = sub

        return sorted_subscriptions

    def _get_pending_total_amount(self):

        sub_filters = self._get_subscriptions_filters('pending')

        subs = Subscription.objects.filter(**sub_filters)

        trans_filters = self._get_transactions_filters('pending')

        trans_filters.update({
            'subscription_id__in': [str(sub.pk) for sub in subs],
        })

        trans_qs_pending = Transaction.objects.filter(**trans_filters)
        trans_qs_pending = trans_qs_pending.exclude(
            subscription__installment_contracts__status__in=[
                Contract.OPEN_STATUS,
                Contract.FULLY_PAID_STATUS,
            ]
        )
        trans_qs_pending = trans_qs_pending.aggregate(
            pending=Sum('liquid_amount')
        )

        total_pending = trans_qs_pending['pending'] or Decimal(0)

        no_trans_subs = subs.annotate(num=Count('transactions'))
        no_trans_subs = no_trans_subs.filter(num=0)

        for sub in no_trans_subs:
            price = sub.lot.get_calculated_price()
            print('- {} = {} - {}'.format(sub.person.name, price, sub.transactions.count()))
            total_pending += price

        print(total_pending)

        return total_pending

    def _get_subscriptions_filters(self, data_type):
        # Inscrições sem contrato e com lotes com preço.
        sub_filter = {
            'event_id': self.event.pk,
            'test_subscription': False,
            'completed': True,
            'lot__price__gt': 0,
            'status':
                Subscription.CONFIRMED_STATUS
                if data_type == 'paid' else Subscription.AWAITING_STATUS,
        }

        return sub_filter

    def _get_transactions_filters(self, data_type):
        trans_filter = {
            'part_id__isnull': True,
            'status': Transaction.PAID
            if data_type == 'paid' else Transaction.WAITING_PAYMENT,
        }

        return trans_filter
