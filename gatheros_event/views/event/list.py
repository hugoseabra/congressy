from datetime import datetime

from django.views.generic import ListView

from gatheros_event.models import Event
from gatheros_event.views.mixins import AccountMixin


class EventListView(AccountMixin, ListView):
    model = Event
    delete_message = "Tem certeza que deseja excluir o evento \"{name}\"?"

    # old template template_name = 'gatheros_event/event/list.html'
    template_name = 'event/list.html'
    ordering = ['name']

    def get_queryset(self):
        queryset = super(EventListView, self).get_queryset()
        return queryset.filter(organization=self.organization)

    def can_access(self):
        return self.is_manager

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = datetime.now()
        return context
