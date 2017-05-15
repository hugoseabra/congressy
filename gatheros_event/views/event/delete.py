from django.urls import reverse_lazy

from core.view.delete import DeleteViewMixin
from gatheros_event.models import Event


class EventDeleteView(DeleteViewMixin):
    model = Event
    template_name = 'gatheros_event/event/delete.html'
    success_url = reverse_lazy('gatheros_event:event-list')

    delete_message = "Não é possível excluir o evento '{name}' possivelmente" \
                     " porque há lotes com inscrições. Exporte, gerencie e" \
                     " exclua os lotes antes de excluir este evento."

    success_message = "Evento excluído com sucesso!"
