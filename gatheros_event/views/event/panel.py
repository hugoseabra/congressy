from datetime import datetime

from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView

from gatheros_event.models import Event
from gatheros_event.views.mixins import AccountMixin


class EventPanelView(AccountMixin, DetailView):
    model = Event
    template_name = 'gatheros_event/event/panel.html'

    def get(self, request, *args, **kwargs):
        event = self.get_object()
        if not self._can_view(event):
            return redirect(reverse_lazy('gatheros_event:event-list'))

        return super(EventPanelView, self).get(request, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(EventPanelView, self).get_context_data(**kwargs)
        context['status'] = self._get_status()
        context['can_change'] = self._can_change
        context['can_delete'] = self._can_delete
        context['can_view_lots'] = self._can_view_lots
        context['percent_attended'] = {
            'label': self.object.percent_attended,
            'number': str(self.object.percent_attended).replace(',', '.'),
        }
        context['report'] = self._get_report()

        return context

    def _can_view(self, event):
        return event.organization == self.organization

    def _can_change(self):
        return self.request.user.has_perm(
            'gatheros_event.change_event',
            self.object
        )

    def _can_delete(self):
        return self.request.user.has_perm(
            'gatheros_event.delete_event',
            self.object
        )

    def _can_view_lots(self):
        subscription_by_lots = \
            self.object.subscription_type == Event.SUBSCRIPTION_BY_LOTS

        can_manage = self.request.user.has_perm(
            'gatheros_event.view_lots',
            self.object
        )

        return subscription_by_lots and can_manage

    def _get_status(self):
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
        now = datetime.now()
        return self.object.date_start - now

    def _get_remaining_days(self, date=None):
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
        """ Recupera relatório do painel"""

        return self.object.get_report()
