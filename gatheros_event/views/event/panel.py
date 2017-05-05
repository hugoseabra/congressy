from django.views.generic import DetailView

from gatheros_event.models import Event


class EventPanelView(DetailView):
    model = Event
    template_name = 'gatheros_event/event/panel.html'
