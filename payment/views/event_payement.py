import locale
from collections import OrderedDict
from decimal import Decimal
from functools import cmp_to_key

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
from installment.models import Contract, Part
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
            if template == 'payments/paid':
                context['subscriptions'] = self.get_payments()
            else:
                context['subscriptions'] = self.get_pending_subscriptions()
        else:
            context['totals'] = {
                'pending': self._get_pending_reports(),
                'paid': self._get_paid_reports(),
            }

        context.update(self.get_event_state_context_data(self.event))

        return context

    def get_payments(self):
        transactions = Transaction.objects.filter(
            subscription__event_id=self.event.pk,
            status=Transaction.PAID,
        )

        subs_dict = OrderedDict()

        for trans in transactions:

            sub_pk = str(trans.subscription_id)

            if sub_pk not in subs_dict:
                sub = trans.subscription

                subs_dict[sub_pk] = OrderedDict()
                subs_dict[sub_pk]['pk'] = sub_pk
                subs_dict[sub_pk]['lot_name'] = sub.lot.name
                subs_dict[sub_pk]['name'] = sub.person.name.upper()
                subs_dict[sub_pk]['transactions'] = list()

            trans_data = {
                'is_boleto': trans.type == Transaction.BOLETO,
                'is_cc': trans.type == Transaction.CREDIT_CARD,
                'is_manual': trans.type == Transaction.MANUAL,
                'type_name': trans.get_type_display(),
                'is_paid': trans.paid is True,
                'is_part': trans.part_id is not None,
                'is_pending': trans.status == Transaction.WAITING_PAYMENT,
                'status_name': trans.get_status_display(),
                'liquid_amount': trans.liquid_amount,
                'part_info': None,
            }

            if trans.part_id:
                part = trans.part

                trans_data['part_info'] = \
                    'parcela {}/{}'.format(
                        part.installment_number,
                        part.contract.num_installments,
                    )

            subs_dict[sub_pk]['transactions'].append(trans_data)

        sub_names = [sub['name'] for _, sub in subs_dict.items()]

        sorted_subscriptions = OrderedDict()

        for name in sorted(sub_names, key=cmp_to_key(locale.strcoll)):
            for _, sub in subs_dict.items():
                if sub['name'] == name:
                    sorted_subscriptions[_] = sub

        return sorted_subscriptions

    def get_pending_subscriptions(self):
        sub_filters = {
            'event_id': self.event.pk,
            'test_subscription': False,
            'completed': True,
            'status': Subscription.AWAITING_STATUS,
            'lot__price__gt': 0,
        }

        subs_dict = OrderedDict()

        subs_qs = Subscription.objects.filter(**sub_filters)

        for sub in subs_qs.order_by(Lower('person__name')):
            contracts_qs = sub.installment_contracts.filter(
                status=Contract.OPEN_STATUS,
            )

            sub_pk = str(sub.pk)
            price = sub.lot.get_liquid_price()

            subs_dict[sub_pk] = {
                'pk': sub.pk,
                'lot_name': sub.lot.name,
                'name': sub.person.name.upper(),
                'liquid_amount': price,
                'part_info': None,
            }

            if contracts_qs.count() > 0:
                contract = contracts_qs.last()
                part = contract.parts.filter(paid=False).first()

                subs_dict[sub_pk]['part_info'] = {
                    'num': contract.num_installments,
                    'part_amount': part.amount,
                }

        sub_names = [sub['name'] for _, sub in subs_dict.items()]

        sorted_subscriptions = OrderedDict()

        for name in sorted(sub_names, key=cmp_to_key(locale.strcoll)):
            for _, sub in subs_dict.items():
                if sub['name'] == name:
                    sorted_subscriptions[_] = sub

        return sorted_subscriptions

    def _get_pending_reports(self):
        sub_filters = {
            'event_id': self.event.pk,
            'test_subscription': False,
            'completed': True,
        }

        total = Subscription.objects.filter(**sub_filters).count()

        sub_filters.update({'lot__price__gt': 0})
        paid_total = Subscription.objects.filter(**sub_filters).count()

        sub_filters.update({'status': Subscription.AWAITING_STATUS})

        subs_qs = Subscription.objects.filter(**sub_filters)
        total_pending = subs_qs.count()

        total_amount = list()
        pending_subs = list()
        pending_part = list()
        origin_internal_amount = list()
        origin_hotsite_amount = list()

        for sub in subs_qs:
            price = sub.lot.get_liquid_price()
            total_amount.append(price)

            if sub.origin in [
                sub.DEVICE_ORIGIN_MANAGE,
                sub.DEVICE_ORIGIN_CSV_IMPORT,
            ]:
                origin_internal_amount.append(price)

            elif sub.origin == sub.DEVICE_ORIGIN_HOTSITE:
                origin_hotsite_amount.append(price)

            contracts_qs = sub.installment_contracts.filter(
                status=Contract.OPEN_STATUS,
            )

            if contracts_qs.count() == 0:
                pending_subs.append(price)

            else:
                pending_part.append(price)

        return {
            'amount': sum(total_amount),
            'total': total_pending,

            'total_general': total,
            'total_payable': paid_total,
            'general_proportion': round((total_pending * 100) / total, 2),
            'payable_proportion': round((total_pending * 100) / paid_total, 2),

            'total_origin_internal': len(origin_internal_amount),
            'total_origin_internal_amount': sum(origin_internal_amount),
            'origin_internal_proportion': round(
                (len(origin_internal_amount) * 100) / total_pending,
                2
            ),
            'total_origin_hotsite': len(origin_hotsite_amount),
            'total_origin_hotsite_amount': sum(origin_internal_amount),
            'origin_hotsite_proportion': round(
                (len(origin_hotsite_amount) * 100) / total_pending,
                2
            ),

            'with_installment': len(pending_part),
            'with_installment_amount': sum(pending_part),
            'with_installment_proportion': round(
                (len(pending_part) * 100) / total_pending,
                2
            ),
            'without_installment_amount': sum(pending_subs),
            'without_installment': len(pending_subs),
            'without_installment_proportion': round(
                (len(pending_subs) * 100) / total_pending,
                2
            ),
        }

    def _get_paid_reports(self):

        sub_filters = {
            'event_id': self.event.pk,
            'test_subscription': False,
            'completed': True,
        }
        total = Subscription.objects.filter(**sub_filters).count()

        sub_filters.update({
            'lot__price__gt': 0,
        })

        subs_qs = Subscription.objects.filter(**sub_filters)
        total_payable = subs_qs.count()

        sub_filters.update({
            'status': Subscription.CONFIRMED_STATUS,
        })
        total_paid = Subscription.objects.filter(**sub_filters).count()

        paid_amounts = list()

        hotsite_amounts = list()
        internal_amounts = list()

        cc_amounts = list()
        boleto_amounts = list()
        manual_amounts = list()
        manual_part_amounts = list()

        method_gateway_amounts = list()
        method_internal_amounts = list()

        installment_cc_amounts = list()
        installment_boletos_amounts = list()
        no_installment_amounts = list()

        transactions_qs = Transaction.objects.filter(
            subscription__event_id=self.event.pk,
        )

        for trans in transactions_qs.filter(status=Transaction.PAID, ):
            amount = trans.liquid_amount
            paid_amounts.append(amount)

            if trans.manual is True:
                if trans.part_id:
                    manual_part_amounts.append(amount)
                else:
                    manual_amounts.append(amount)

                method_internal_amounts.append(amount)

            elif trans.type == Transaction.CREDIT_CARD:
                cc_amounts.append(amount)
                method_gateway_amounts.append(amount)
            elif trans.type == Transaction.BOLETO:
                boleto_amounts.append(amount)
                method_gateway_amounts.append(amount)

            if trans.installments > 1 and trans.type == trans.CREDIT_CARD:
                installment_cc_amounts.append(amount)
            elif trans.part_id:
                installment_boletos_amounts.append(amount)
            else:
                no_installment_amounts.append(amount)

            sub = trans.subscription

            if sub.origin == Subscription.DEVICE_ORIGIN_HOTSITE:
                hotsite_amounts.append(amount)
            elif sub.origin in [
                Subscription.DEVICE_ORIGIN_CSV_IMPORT,
                Subscription.DEVICE_ORIGIN_MANAGE,
            ]:
                internal_amounts.append(amount)

        return {
            'amount': sum(paid_amounts),

            'total': total_paid,
            'total_general': total,
            'total_payable': total_payable,
            'payable': total_payable,
            'general_proportion': round(
                (total_paid * 100) / total,
                2
            ),
            'payable_proportion': round(
                (total_paid * 100) / total_payable,
                2
            ),

            'total_origin_internal': len(internal_amounts),
            'origin_internal_amount': sum(internal_amounts),
            'origin_internal_proportion': round(
                (len(internal_amounts) * 100) / len(paid_amounts),
                2
            ),
            'total_origin_hotsite': len(hotsite_amounts),
            'origin_hotsite_amount': sum(hotsite_amounts),
            'origin_hotsite_proportion': round(
                (len(hotsite_amounts) * 100) / len(paid_amounts),
                2
            ),

            'cc_total': len(cc_amounts),
            'cc_amount': sum(cc_amounts),
            'cc_proportion': round(
                (len(cc_amounts) * 100) / len(paid_amounts),
                2
            ),
            'boleto_total': len(boleto_amounts),
            'boleto_amount': sum(boleto_amounts),
            'boleto_proportion': round(
                (len(boleto_amounts) * 100) / len(paid_amounts),
                2
            ),
            'manual_installment_total': len(manual_part_amounts),
            'manual_installment_amount': sum(manual_part_amounts),
            'manual_installment_proportion': round(
                (len(manual_part_amounts) * 100) / len(paid_amounts),
                2
            ),
            'manual_no_installment_total': len(manual_amounts),
            'manual_no_installment_amount': sum(manual_amounts),
            'manual_no_installment_proportion': round(
                (len(manual_amounts) * 100) / len(paid_amounts),
                2
            ),

            'gateway_method_total': len(method_gateway_amounts),
            'gateway_method_amount': sum(method_gateway_amounts),
            'gateway_method_proportion': round(
                (len(method_gateway_amounts) * 100) / len(paid_amounts),
                2
            ),
            'manual_method_total': len(method_internal_amounts),
            'manual_method_amount': sum(method_internal_amounts),
            'manual_method_proportion': round(
                (len(method_internal_amounts) * 100) / len(paid_amounts),
                2
            ),

            'with_installment_boleto': len(installment_boletos_amounts),
            'with_installment_boleto_amount': sum(installment_boletos_amounts),
            'with_installment_boleto_proportion': round(
                (len(installment_boletos_amounts) * 100) / len(paid_amounts),
                2
            ),
            'with_installment_cc': len(installment_cc_amounts),
            'with_installment_cc_amount': sum(installment_cc_amounts),
            'with_installment_cc_proportion': round(
                (len(installment_cc_amounts) * 100) / len(paid_amounts),
                2
            ),
            'without_installment': len(no_installment_amounts),
            'without_installment_amount': sum(no_installment_amounts),
            'without_installment_proportion': round(
                (len(no_installment_amounts) * 100) / len(paid_amounts),
                2
            ),
        }
