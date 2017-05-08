from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from core.view.user_context import UserContextViewMixin
from gatheros_event.models import Event, Member


class EventListView(LoginRequiredMixin, UserContextViewMixin, ListView):
    model = Event
    template_name = 'gatheros_event/event/list.html'
    ordering = ['name']

    def get_queryset( self ):
        qs = super(EventListView, self).get_queryset()

        # Super user vê tudo
        if self.user_context.get('superuser', False):
            return qs

        try:
            return qs.filter(
                organization__pk=self.user_context['active_organization']['pk']
            )
        except TypeError:
            pass

    def get_context_data( self, **kwargs ):
        context = super(EventListView, self).get_context_data(**kwargs)
        context.update(self.get_event_list_context())
        return context

    def get_event_list_context( self ):
        member_group = self.user_context.get('active_member_group')

        def can_add():
            return self.user_context.get('superuser', False) or (
                member_group and member_group['group'] in [
                    Member.ADMIN,
                ]
            )

        def can_edit():
            return self.user_context.get('superuser', False) or (
                member_group and member_group['group'] in [
                    Member.ADMIN,
                    Member.HELPER,
                ]
            )

        def can_delete():
            return self.user_context.get('superuser', False) or (
                member_group and member_group['group'] == Member.ADMIN
            )

        return {
            'can_add': can_add,
            'can_edit': can_edit,
            'can_delete': can_delete,
        }
