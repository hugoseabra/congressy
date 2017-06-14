from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView

from gatheros_event.models import Organization
from gatheros_event.views.mixins import AccountMixin


class OrganizationListView(AccountMixin, ListView):
    model = Organization
    template_name = 'gatheros_event/organization/list.html'
    ordering = ['name']

    def dispatch(self, request, *args, **kwargs):
        if not self._can_view():
            messages.warning(request, 'Você não pode acessar esta área.')
            return redirect(reverse_lazy('gatheros_front:start'))

        dispatch = super(OrganizationListView, self).dispatch(
            request,
            *args,
            **kwargs
        )

        return dispatch

    def get_queryset(self):
        query_set = super(OrganizationListView, self).get_queryset()
        person = self.member.person
        return query_set.filter(
            internal=False,
            members__person=person
        ).distinct()

    def _can_view(self):
        return not self.is_participant
