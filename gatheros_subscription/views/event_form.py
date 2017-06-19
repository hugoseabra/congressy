from django.views import generic
from django.shortcuts import get_object_or_404

from gatheros_event.models import Event
from gatheros_subscription.forms import EventForm


class EventFormView(generic.FormView):
    form_class = EventForm
    template_name = 'gatheros_subscription/event_form.html'
    event = None

    def get_context_data(self, **kwargs):
        context = super(EventFormView, self).get_context_data(**kwargs)
        context.update({
            'event': self._get_event(),
            'form_title': 'Configuração de Formulário',
        })
        return context

    def get_form(self, form_class=None):
        if not form_class:
            form_class = self.form_class
        
        return form_class(
            event=self._get_event(),
            **self.get_form_kwargs()
        )
    
    def _get_event(self):
        if not self.event:
            pk = self.kwargs.get('event_pk')
            self.event = get_object_or_404(Event, pk=pk)
        
        return self.event
