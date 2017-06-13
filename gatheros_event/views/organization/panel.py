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

    def get_context_data(self, **kwargs):
        context = super(OrganizationPanelView, self).get_context_data(**kwargs)
        context.update({
            'can_manage': self._can_manage,
            'can_manage_places': self._can_manage_places,
            'can_manage_invitations': self._can_manage_invitations,
            'can_change': self._can_change,
            'can_delete': self._can_delete,
        })
        return context

    def _can_manage_places(self):
        return self.request.user.has_perm(
            'gatheros_event.can_add_place',
            self.organization
        )

    def _can_manage_invitations(self):
        return self.request.user.has_perm(
            'gatheros_event.can_invite',
            self.organization
        )

    def _can_manage(self):
        return self._can_manage_invitations() or self._can_manage_places()

    def _can_change(self):
        return self.request.user.has_perm(
            'gatheros_event.change_organization',
            self.organization
        )

    def _can_delete(self):
        return self.request.user.has_perm(
            'gatheros_event.delete_organization',
            self.organization
        )

    def _can_view(self):
        if self.is_participant:
            return False

        return self.organization.internal is False
