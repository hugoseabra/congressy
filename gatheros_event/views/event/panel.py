from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView

from gatheros_event.models import Event


class EventPanelView(LoginRequiredMixin, DetailView):
    model = Event
    template_name = 'gatheros_event/event/panel.html'
