from django.urls import reverse_lazy
from django.utils.module_loading import import_string

from gatheros_event.models import Event

DeleteViewMixin = import_string('core.view.delete.DeleteViewMixin')


class EventDeleteView(DeleteViewMixin):
    model = Event
    success_url = reverse_lazy('gatheros_event:event-list')

    delete_message = "Não é possível excluir o evento '{name}' possivelmente" \
                     " porque há lotes com inscrições. Exporte, gerencie e" \
                     " exclua os lotes antes de excluir este evento."

    success_message = "Evento excluído com sucesso!"

    def get_context_data(self, **kwargs):
        context = super(EventDeleteView, self).get_context_data(**kwargs)
        context['next_path'] = self._get_referer_url()

        return context

    def _get_referer_url(self):
        request = self.request
        previous_url = request.META.get('HTTP_REFERER')
        if previous_url:
            host = request.scheme+'://'+request.META.get('HTTP_HOST', '')
            previous_url = previous_url.replace(host, '')

            if previous_url != request.path:
                return previous_url

        return self.success_url
