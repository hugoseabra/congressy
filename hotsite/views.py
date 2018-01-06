from datetime import datetime

from django.shortcuts import render
from django.views.generic import DetailView, FormView
from gatheros_event.forms import ProfileCreateForm
from gatheros_event.models import Event, Info, Person


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


class HotsiteFormView(DetailView):
    template_name = 'hotsite/form.html'
    form = ProfileCreateForm

    def post(self, request, *args, **kwargs):

        if self.request.POST.get('name'):

            name = self.request.POST.get('name')
            email = self.request.POST.get('email')

            form = ProfileCreateForm(data={"name": name, "email": email})

            if form.is_valid():
                form.save()
            else:
                print('hi')
                for error in form.errors:
                    print(error)
                    print('er')
                    """ START HERE"""
            person = Person.objects.get(email=email)

            object_pk = kwargs['pk']

            obj = Event.objects.get(pk=object_pk)
            info = Info.objects.get(pk=object_pk)

            period = obj.get_period()
            return render(request, self.template_name, {"name": name,
                                                        "email": email,
                                                        "object": obj,
                                                        "info": info,
                                                        "peron": person,
                                                        "period": period,
                                                        })
