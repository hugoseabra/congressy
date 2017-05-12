from django.urls import reverse_lazy

from core.view.delete import DeleteViewMixin
from gatheros_event.models import Event, Member


class EventDeleteView(DeleteViewMixin):
    model = Event
    template_name = 'gatheros_event/event/delete.html'
    success_url = reverse_lazy('gatheros_event:event-list')

    delete_message = "Não é possível excluir o evento '{name}' possivelmente" \
                     " porque há lotes com inscrições. Exporte, gerencie e" \
                     " exclua os lotes antes de excluir este evento."

    not_allowed_message = "Você não tem permissão para excluir este evento"

    success_message = "Evento excluído com sucesso!"

    def can_delete(self):
        event = self.get_object()
        organization = event.organization
        active = self.user_context.active_organization

        return organization.pk == active.pk and active.group == Member.ADMIN
