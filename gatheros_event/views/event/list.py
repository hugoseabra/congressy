from django.views.generic import ListView

from gatheros_event.models import Event
from gatheros_event.views.mixins import AccountMixin


class EventListView(AccountMixin, ListView):
    model = Event
    template_name = 'gatheros_event/event/list.html'
    ordering = ['name']

    def get_template_names(self):
        if self.request.user.is_superuser:
            return ['gatheros_event/event/list_superuser.html']

        return [self.template_name]

    def get_queryset(self):
        query_set = super(EventListView, self).get_queryset()

        if self.request.user.is_superuser:
            return query_set

        return query_set.filter(organization=self.organization)
