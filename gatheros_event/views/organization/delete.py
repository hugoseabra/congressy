from django.contrib import messages
from django.urls import reverse_lazy

from core.view.delete import DeleteViewMixin
from gatheros_event.models import Organization


class OrganizationDeleteView(DeleteViewMixin):
    model = Organization
    delete_message = 'Tem certeza que deseja excluir a organização "{name}"?'
    success_message = 'Organização excluída com sucesso.'
    success_url = reverse_lazy('gatheros_event:organization-list')

    def dispatch(self, request, *args, **kwargs):
        can_delete = self.can_delete()

        dispatch = super(OrganizationDeleteView, self).dispatch(
            request,
            *args,
            **kwargs
        )

        if not can_delete:
            event_list = self._get_related_events()
            if event_list:
                msg = 'Os seguintes eventos estão relacionados a este local: '
                msg += ', '.join(event_list)
                messages.warning(request, msg)

        return dispatch

    def _get_related_events(self):
        event_list = []
        for e in self.object.events.all():
            event_list.append('"{} (ID: {})"'.format(e.name, e.pk))

        return event_list
