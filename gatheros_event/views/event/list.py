from django.views.generic import ListView

from gatheros_event.models import Event
from gatheros_event.views.mixins import AccountMixin


class EventListView(AccountMixin, ListView):
    model = Event
    template_name = 'gatheros_event/event/list.html'
    ordering = ['name']

    def get_queryset(self):
        query_set = super(EventListView, self).get_queryset()
        return query_set.filter(organization=self.organization)
