from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView

from gatheros_event.models import Organization
from gatheros_event.views.mixins import AccountMixin


class OrganizationPanelView(AccountMixin, DetailView):
    model = Organization
    template_name = 'gatheros_event/organization/panel.html'

    def dispatch(self, request, *args, **kwargs):
        dispatch = super(OrganizationPanelView, self).dispatch(
            request,
            *args,
            **kwargs
        )
        if self.organization and not self._can_view():
            messages.warning(
                request,
                'Você não tem permissão de realizar esta ação.'
            )
            return redirect(reverse_lazy('gatheros_front:start'))

        return dispatch

    def get_context_data(self, **kwargs):
        context = super(OrganizationPanelView, self).get_context_data(**kwargs)

        # Força valor de contexto
        context['organization'] = self.organization
        context.update({
            'invitations': self._get_invitations(),
            'events': self.object.events.all()[0:6],
            'can_manage_places': self._can_manage_places,
            'can_manage_invitations': self._can_manage_invitations,
            'can_manage_members': self._can_manage_members,
            'can_change': self._can_change,
            'can_delete': self._can_delete,
        })
        return context

    def _get_invitations(self):
        return self.object.get_invitations(include_expired=False, limit=5)

    def _can_manage_places(self):
        return self.request.user.has_perm(
            'gatheros_event.can_manage_places',
            self.object
        )

    def _can_manage_invitations(self):
        return self.request.user.has_perm(
            'gatheros_event.can_invite',
            self.object
        )

    def _can_manage_members(self):
        return self.request.user.has_perm(
            'gatheros_event.can_manage_members',
            self.object
        )

    def _can_change(self):
        return self.request.user.has_perm(
            'gatheros_event.change_organization',
            self.object
        )

    def _can_delete(self):
        return self.object.is_deletable() and self.request.user.has_perm(
            'gatheros_event.delete_organization',
            self.object
        )

    def _can_view(self):
        if self.is_participant:
            return False

        org = self.get_object()
        user = self.request.user
        member = org.get_member(user)

        return org.internal is False and member and member.active
