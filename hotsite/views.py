from datetime import datetime

from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import DetailView

from gatheros_event.models import Event, Info
from gatheros_event.views.mixins import AccountMixin


def hotsite_base(request):
    return render(request, 'hotsite/base.html')


def hotsite_form(request):
    return render(request, 'hotsite/form.html')


class HotsiteView(DetailView):
    # @TODO Use slug instead of PK to find event
    model = Event
    template_name = 'hotsite/base.html'

    def get_context_data(self, **kwargs):
        context = super(HotsiteView, self).get_context_data(**kwargs)
        context['status'] = self._get_status()
        context['report'] = self._get_report()
        context['period'] = self._get_period()
        context['info'] = Info.objects.get(pk=self.object.pk)
        return context

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

    def _get_period(self):
        """ Resgata o prazo de duração do evento. """
        return self.object.get_period()

