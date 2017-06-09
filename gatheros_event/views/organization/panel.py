from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from gatheros_event.views.mixins import AccountMixin


# @TODO Restringir visualização

class OrganizationPanelView(AccountMixin, TemplateView):
    template_name = 'gatheros_event/organization/panel.html'

    def dispatch(self, request, *args, **kwargs):
        dispatch = super(OrganizationPanelView, self).dispatch(
            request,
            *args,
            **kwargs
        )
        if not self._can_view():
            messages.warning(request, 'Você não está em uma organização.')
            return redirect(reverse_lazy('gatheros_front:start'))

        return dispatch

    def _can_view(self):
        return self.organization.internal is False
