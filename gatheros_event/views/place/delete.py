from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.urls import reverse

from gatheros_event.models import Organization, Place
from gatheros_event.views.mixins import DeleteViewMixin


class PlaceDeleteView(DeleteViewMixin):
    model = Place
    delete_message = 'Tem certeza que deseja excluir o local "{name}"?'
    success_message = 'Local excluído com sucesso.'
    place_organization = None

    def dispatch(self, request, *args, **kwargs):
        can_delete = self.can_delete()

        dispatch = super(PlaceDeleteView, self).dispatch(
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

    def get_place_organization(self):
        if self.place_organization:
            return self.place_organization

        self.place_organization = get_object_or_404(
            Organization,
            pk=self.kwargs.get('organization_pk')
        )
        return self.place_organization

    def get_success_url(self):
        org = self.get_place_organization()
        return reverse('gatheros_event:place-list', kwargs={
            'organization_pk': org.pk
        })

    def _get_related_events(self):
        event_list = []
        for e in self.object.events.all():
            event_list.append('"{} (ID: {})"'.format(e.name, e.pk))

        return event_list
