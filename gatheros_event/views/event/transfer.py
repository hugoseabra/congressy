from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import FormView

from gatheros_event.forms import EventTransferForm
from gatheros_event.models import Event
from ..mixins import AccountMixin


class EventTransferView(AccountMixin, FormView):
    """ View para transferência de propriedade de evento. """

    success_message = "Evento transferido com sucesso."
    template_name = 'gatheros_event/event/transfer_form.html'
    object = None
    error_messages = []

    def form_valid(self, form):
        if form.is_valid():
            form.save()
            messages.success(self.request, 'Evento transferido com sucesso.')

        return super(EventTransferView, self).form_valid(form)

    def get_form(self, form_class=None):
        self.object = get_object_or_404(Event, pk=self.kwargs.get('pk'))
        
        return EventTransferForm(
            user=self.request.user,
            instance=self.object,
            **self.get_form_kwargs()
        )

    def get_context_data(self, **kwargs):
        context = super(EventTransferView, self).get_context_data(**kwargs)
        context.update({
            'form_title': 'Transferênca de evento',
            'object': self.object,
        })

        return context

    def get_success_url(self):
        return reverse_lazy('gatheros_event:event-list')
