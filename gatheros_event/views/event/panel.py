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
        if self._cannot_view(event):
            return redirect(reverse_lazy('gatheros_event:event-list'))

        return super(EventPanelView, self).get(request, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(EventPanelView, self).get_context_data(**kwargs)
        context['status'] = self._get_status()
        context['can_change'] = self._can_change
        context['can_delete'] = self._can_delete

        return context

    def _cannot_view(self, event):
        can = event.organization == self.organization
        return can is False

    def _can_change(self):
        return self.request.user.has_perm(
            'gatheros_event.change_event',
            self.object
        )

    def _can_delete(self):
        can = self.request.user.has_perm(
            'gatheros_event.delete_event',
            self.object
        )
        return can and self.object.is_deletable()

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
