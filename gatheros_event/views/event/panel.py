from datetime import datetime
from decimal import Decimal
from django.db.models import Q
from django.shortcuts import get_object_or_404

from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import DetailView

from gatheros_event.helpers.account import update_account
from gatheros_event.models import Event
from gatheros_subscription.models import Subscription
from gatheros_event.views.mixins import AccountMixin
from payment.models import Transaction, TransactionStatus


class EventPanelView(AccountMixin, DetailView):
    model = Event
    # template_name = 'gatheros_event/event/panel.html'
    template_name = 'event/panel.html'
    permission_denied_url = reverse_lazy('event:event-list')
    object = None

    def pre_dispatch(self, request):
        self.object = self.get_object()

        if self.object:
            update_account(
                request=self.request,
                organization=self.object.organization,
                force=True
            )

        return super().pre_dispatch(request)

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.event = get_object_or_404(Event, pk=self.kwargs.get('pk'))

        # return redirect(reverse('subscription:subscription-list', kwargs={
        #     'event_pk': self.object.pk
        # }))

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(EventPanelView, self).get_context_data(**kwargs)
        context['status'] = self._get_status()
        context['totals'] = self._get_payables()
        context['limit'] = self._get_limit()
        context['has_paid_lots'] = self.has_paid_lots()
        context['gender'] = self._get_gender()
        context['pending'] = self._get_number_pending()
        context['has_inside_bar'] = True
        context['active'] = 'panel'
        context['total_subscriptions'] = self._get_total_subscriptions()
        context['can_transfer'] = self._can_transfer
        context['can_change'] = self._can_change
        context['can_delete'] = self._can_delete
        context['can_view_lots'] = self._can_view_lots
        context['can_manage_subscriptions'] = self.can_manage_subscriptions
        context['percent_attended'] = {
            'label': round(self.object.percent_attended),
            'number': str(self.object.percent_attended).replace(',', '.'),
        }
        context['report'] = self._get_report()

        return context

    def has_paid_lots(self):
        """ Retorna se evento possui algum lote pago. """
        for lot in self.event.lots.all():
            price = lot.price
            if price is None:
                continue

            if lot.price > 0:
                return True

        return False

    def _get_gender(self):
        return self.event.get_report()

    def _get_limit(self):
        return self.event.limit

    def _get_total_subscriptions(self):
        return self.event.subscriptions.count()

    def can_access(self):
        event = self.get_object()
        return event.organization == self.organization

    def _can_transfer(self):
        """ Verifica se usuário pode transferir este evento. """
        return self.is_organization_admin

    def _can_change(self):
        """ Verifica se usuário pode alterar o evento. """
        return self.request.user.has_perm(
            'gatheros_event.change_event',
            self.object
        )

    def _can_delete(self):
        """ Verifica se usuário pode excluir o evento. """
        return self.object.is_deletable() and self.request.user.has_perm(
            'gatheros_event.delete_event',
            self.object
        )

    def _can_view_lots(self):
        """ Verifica se usuário pode visualizar lotes. """
        subscription_by_lots = \
            self.object.subscription_type == Event.SUBSCRIPTION_BY_LOTS

        can_manage = self.request.user.has_perm(
            'gatheros_event.view_lots',
            self.object
        )

        return subscription_by_lots and can_manage

    def can_manage_subscriptions(self):
        """ Verifica se usuário pode gerenciar inscrições. """
        return self.request.user.has_perm(
            'gatheros_subscription.can_manage_subscriptions',
            self.object
        )

    def _get_status(self):
        """ Resgata o status. """
        now = datetime.now()
        event = self.object
        remaining = self._get_remaining_datetime()
        remaining_str = self._get_remaining_days(date=remaining)

        result = {
            'published': event.published,
        }

        future = event.date_start > now
        running = event.date_start <= now <= event.date_end
        finished = now >= event.date_end

        if future:
            result.update({
                'status': 'future',
                'remaining': remaining_str,
            })

        elif running:
            result.update({
                'status': 'running',
            })

        elif finished:
            result.update({
                'status': 'finished' if event.published else 'expired',
            })

        return result

    def _get_remaining_datetime(self):
        """ Resgata diferença de tempo que falta para o evento finalizar. """
        now = datetime.now()
        return self.object.date_start - now

    def _get_remaining_days(self, date=None):
        """ Resgata tempo que falta para o evento finalizar em dias. """
        now = datetime.now()

        if not date:
            date = self._get_remaining_datetime()

        remaining = ''

        days = date.days
        if days > 0:
            remaining += str(date.days) + 'dias '

        remaining += str(int(date.seconds / 3600)) + 'h '
        remaining += str(60 - now.minute) + 'm'

        return remaining

    def _get_report(self):
        """ Resgata informações gerais do evento. """
        return self.object.get_report()

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

    def _get_number_pending(self):

        pending = \
            Subscription.objects.filter(
                status=Subscription.AWAITING_STATUS,
                event=self.event
            ).count()

        return pending
