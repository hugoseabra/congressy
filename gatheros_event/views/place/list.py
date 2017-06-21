from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import ListView

from gatheros_event.models import Organization, Place
from gatheros_event.views.mixins import AccountMixin


class PlaceListView(AccountMixin, ListView):
    model = Place
    template_name = 'gatheros_event/place/list.html'
    place_organization = None

    def get_context_data(self, **kwargs):
        context = super(PlaceListView, self).get_context_data(**kwargs)
        context['place_organization'] = self.get_place_organization()

        return context

    def dispatch(self, request, *args, **kwargs):
        if not self._can_view():
            org = self.get_place_organization()
            messages.warning(
                request,
                'Você não tem permissão de realizar esta ação.'
            )
            return redirect(reverse(
                'gatheros_event:organization-panel',
                kwargs={'pk': org.pk}
            ))

        return super(PlaceListView, self).dispatch(
            request,
            *args,
            **kwargs
        )

    def get_queryset(self):
        query_set = super(PlaceListView, self).get_queryset()
        organization = self.get_place_organization()

        return query_set.filter(organization=organization)

    def get_place_organization(self):
        """ Resgata organização do contexto da view. """

        if self.place_organization:
            return self.place_organization

        self.place_organization = get_object_or_404(
            Organization,
            pk=self.kwargs.get('organization_pk')
        )
        return self.place_organization

    def _can_view(self):
        not_participant = not self.is_participant
        can_manage = self.request.user.has_perm(
            'gatheros_event.can_manage_places',
            self.get_place_organization()
        )
        return not_participant and can_manage
