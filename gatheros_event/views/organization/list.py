from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView

from gatheros_event.models import Organization
from gatheros_event.views.mixins import AccountMixin


class OrganizationListView(AccountMixin, ListView):
    model = Organization
    # template_name = 'gatheros_event/organization/list.html'
    template_name = 'organization/list.html'
    ordering = ['name']

    def dispatch(self, request, *args, **kwargs):
        dispatch = super(OrganizationListView, self).dispatch(
            request,
            *args,
            **kwargs
        )

        if self.organization and not self._can_view():
            messages.warning(
                request,
                'Você não tem permissão de realizar esta ação.'
            )
            return redirect(reverse_lazy('front:start'))

        return dispatch

    def get_queryset(self):
        query_set = super(OrganizationListView, self).get_queryset()
        person = self.member.person
        return query_set.filter(
            internal=False,
            members__person=person,
            members__active=True,
        ).distinct()

    def _can_view(self):
        return self.is_manager
