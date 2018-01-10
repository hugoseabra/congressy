from django.contrib import messages
from django.urls import reverse_lazy

from gatheros_event.models import Organization
from gatheros_event.views.mixins import DeleteViewMixin
from gatheros_event.helpers.account import update_account


class OrganizationDeleteView(DeleteViewMixin):
    template_name = "organization/delete.html"
    model = Organization
    delete_message = 'Tem certeza que deseja excluir a organização "{name}"?'
    success_message = 'Organização excluída com sucesso.'
    success_url = reverse_lazy('event:event-list')

    def dispatch(self, request, *args, **kwargs):
        can_delete = self.can_delete()

        dispatch = super(OrganizationDeleteView, self).dispatch(
            request,
            *args,
            **kwargs
        )

        if self.organization and not can_delete:
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

    def post_delete(self):
        update_account(self.request)

