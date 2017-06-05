from django.views.generic import DetailView

from gatheros_event.models import Event
from gatheros_event.views.mixins import AccountMixin


class EventDetaillView(AccountMixin, DetailView):
    model = Event
    template_name = 'gatheros_event/event/detail.html'
