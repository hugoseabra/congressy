import absoluteuri

from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views import generic

from gatheros_event.models import Event
from gatheros_event.views.mixins import AccountMixin


class EventViewMixin(AccountMixin, generic.View):
    """ Mixin de view para vincular com informações de event. """
    event = None
    permission_denied_url = reverse_lazy('event:event-list')

    def dispatch(self, request, *args, **kwargs):
        self.event = self.get_event()
        return super(EventViewMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # noinspection PyUnresolvedReferences
        context = super(EventViewMixin, self).get_context_data(**kwargs)
        context['event'] = self.get_event()
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

    def can_access(self):
        if not self.event:
            return False

        return self.event.organization == self.organization

