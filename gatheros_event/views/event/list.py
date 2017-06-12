from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy

from django.views.generic import ListView

from gatheros_event.models import Event
from gatheros_event.views.mixins import AccountMixin


class EventListView(AccountMixin, ListView):
    model = Event
    template_name = 'gatheros_event/event/list.html'
    ordering = ['name']

    def dispatch(self, request, *args, **kwargs):
        if not self._can_view():
            messages.warning(request, 'Você não pode acessar esta área.')
            return redirect(reverse_lazy('gatheros_front:start'))

        dispatch = super(EventListView, self).dispatch(
            request,
            *args,
            **kwargs
        )

        return dispatch

    def get_queryset(self):
        query_set = super(EventListView, self).get_queryset()
        return query_set.filter(organization=self.organization)

    def _can_view(self):
        return not self.is_participant
