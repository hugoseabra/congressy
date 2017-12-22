from datetime import datetime

from django.urls import reverse_lazy
from django.views.generic import DetailView

from gatheros_event.models import Event
from gatheros_event.views.mixins import AccountMixin


class EventPanelView(AccountMixin, DetailView):
    model = Event
    # template_name = 'gatheros_event/event/panel.html'
    template_name = 'event/dashboard.html'
    permission_denied_url = reverse_lazy('event:event-list')

    def get_context_data(self, **kwargs):
        context = super(EventPanelView, self).get_context_data(**kwargs)
        context['status'] = self._get_status()
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
