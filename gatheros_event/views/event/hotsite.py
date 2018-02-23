from django.contrib import messages
from django.shortcuts import reverse, get_object_or_404
from django.views.generic import FormView

from gatheros_event import forms
from gatheros_event.helpers.account import update_account
from gatheros_event.models import Event, Info
from gatheros_event.views.mixins import AccountMixin


class EventHotsiteView(AccountMixin, FormView):
    form_class = forms.HotsiteForm
    template_name = 'event/hotsite.html'
    event = None
    object = None

    def can_access(self):
        if not self.event:
            return False

        return self.event.organization == self.organization

    def get_permission_denied_url(self):
        return reverse('event:event-list')

    def pre_dispatch(self, request):
        event = self._get_event()

        update_account(
            request=self.request,
            organization=event.organization,
            force=True
        )

        return super().pre_dispatch(request)

    def _get_event(self):
        if self.event:
            return self.event

        self.event = get_object_or_404(Event, pk=self.kwargs.get('pk'))
        return self.event

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        event = self._get_event()
        kwargs['event'] = event

        try:
            kwargs['instance'] = event.info
        except Info.DoesNotExist:
            pass

        return kwargs

    def form_valid(self, form):
        messages.success(
            self.request,
            "Configurações de páginas atualizadas com sucesso."
        )
        self.object = form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        event = self._get_event()

        context = super(EventHotsiteView, self).get_context_data(**kwargs)
        context['event'] = event
        context['has_paid_lots'] = self.has_paid_lots()

        try:
            context['info'] = event.info
        except Info.DoesNotExist:
            pass

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

    def get_success_url(self):
        return reverse('event:event-hotsite', kwargs={
            'pk': self.kwargs['pk']
        })
