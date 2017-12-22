from django.views.generic import ListView

from gatheros_event.models import Event
from gatheros_event.views.mixins import AccountMixin


class EventListView(AccountMixin, ListView):
    model = Event
    # old template template_name = 'gatheros_event/event/list.html'
    template_name = 'event/list.html'
    ordering = ['name']

    def get_queryset(self):
        queryset = super(EventListView, self).get_queryset()
        return queryset.filter(organization=self.organization)

    def can_access(self):
        return self.is_manager
