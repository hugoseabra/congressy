from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from core.view.organization_context_check import OrganizationContextCheckMixin
from gatheros_event.models import Event, Member


class EventListView(LoginRequiredMixin, OrganizationContextCheckMixin, ListView):
    model = Event
    template_name = 'gatheros_event/event/list.html'
    ordering = ['name']

    def get_queryset( self ):
        qs = super(EventListView, self).get_queryset()

        # Super user vê tudo
        if self.super_user:
            return qs

        return qs.filter(organization__pk=self.organization.get('pk'))

    def get_context_data( self, **kwargs ):
        context = super(EventListView, self).get_context_data(**kwargs)
        context.update(self.get_event_list_context())
        context.update(self.get_organization_context())
        return context

    def get_event_list_context( self ):
        def can_edit():
            return self.super_user or (self.member_group and self.member_group['group'] in [
                Member.ADMIN,
                Member.HELPER
            ])

        def can_delete():
            return self.super_user or (self.member_group and self.member_group['group'] == Member.ADMIN)

        return {
            'can_edit': can_edit,
            'can_delete': can_delete,
        }
