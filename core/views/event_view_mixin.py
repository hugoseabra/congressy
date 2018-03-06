from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import generic

from gatheros_event.helpers.account import update_account
from gatheros_event.models import Event
from gatheros_event.views.mixins import (
    AccountMixin,
)


class EventViewMixin(AccountMixin, generic.View):
    """ Mixin de view para vincular com informações de event. """
    event = None

    def dispatch(self, request, *args, **kwargs):
        event = self.get_event()

        update_account(
            request=self.request,
            organization=event.organization,
            force=True
        )

        self.permission_denied_url = reverse(
            'event:event-panel',
            kwargs={'pk': self.kwargs.get('event_pk')}
        )
        return super(EventViewMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # noinspection PyUnresolvedReferences
        context = super(EventViewMixin, self).get_context_data(**kwargs)
        context['event'] = self.get_event()
        context['has_paid_lots'] = self.has_paid_lots()

        return context

    def get_event(self):
        """ Resgata organização do contexto da view. """

        if self.event:
            return self.event

        self.event = get_object_or_404(
            Event,
            pk=self.kwargs.get('event_pk')
        )
        return self.event

    def has_paid_lots(self):
        """ Retorna se evento possui algum lote pago. """
        for lot in self.event.lots.all():

            price = lot.price

            if price and price > 0:
                return True

        return False

    def can_access(self):
        return self.get_event().organization == self.organization

    def get_permission_denied_url(self):
        return reverse('event:event-list')
