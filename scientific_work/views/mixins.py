from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic

from gatheros_event.models import Event
from gatheros_event.views.mixins import AccountMixin
from gatheros_subscription.models import Subscription


class WorkViewMixin(AccountMixin, generic.View):
    subscription = None

    def dispatch(self, request, *args, **kwargs):
        subscription_pk = self.kwargs.get('subscription_pk')
        if not subscription_pk:
            messages.error(self.request, 'Não foi possivel resgatar a '
                                         'inscrição.')
            return redirect(reverse_lazy('front:start'))

        self.subscription = get_object_or_404(Subscription, pk=subscription_pk)
        response = super().dispatch(request, *args, **kwargs)

        return response


class EventViewMixin(AccountMixin, generic.View):
    event = None

    def dispatch(self, request, *args, **kwargs):
        event_pk = self.kwargs.get('pk')
        if not event_pk:
            messages.error(self.request,
                           'Não foi possivel resgatar a buscar a página.')
            return redirect(reverse_lazy('front:start'))

        self.event = get_object_or_404(Event, pk=event_pk)
        response = super().dispatch(request, *args, **kwargs)

        return response