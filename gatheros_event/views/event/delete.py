from django.urls import reverse_lazy

from gatheros_event.models import Event
from gatheros_event.views.mixins import DeleteViewMixin


class EventDeleteView(DeleteViewMixin):
    """ View de exclusão de Event. """
    model = Event
    success_url = reverse_lazy('event:event-list')
    delete_message = "Tem certeza que deseja excluir o evento \"{name}\"?"
    success_message = "Evento excluído com sucesso."
    template_name = "event/delete.html"

    def get_permission_denied_url(self):
        return self.success_url

    def get_context_data(self, **kwargs):
        context = super(EventDeleteView, self).get_context_data(**kwargs)
        context['next_path'] = self._get_referer_url()

        return context

    def _get_referer_url(self):
        """ Recupera url anterior para redirecionamento. """
        request = self.request
        previous_url = request.META.get('HTTP_REFERER')

        if not previous_url:
            return self.success_url

        host = request.scheme + '://' + request.META.get('HTTP_HOST', '')
        previous_url = previous_url.replace(host, '')

        if previous_url != request.path:
            return previous_url
