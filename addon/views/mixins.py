from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import generic

from gatheros_event.models import Event
from gatheros_event.views.mixins import AccountMixin, EventDraftStateMixin


class OptionalBaseMixin(AccountMixin, generic.View, EventDraftStateMixin):
    event = None
    permission_denied_message = 'Você não pode realizar esta ação.'

    def get_permission_denied_url(self):
        return reverse(
            'event:event-panel',
            kwargs={
                'pk': self.event.pk,
            }
        )

    def pre_dispatch(self, request):
        self.event = get_object_or_404(
            Event,
            pk=self.kwargs.get('event_pk'),
        )

        return super().pre_dispatch(request)

    def get_context_data(self, **kwargs):
        # noinspection PyUnresolvedReferences
        context = super().get_context_data(**kwargs)
        context['event'] = self.event

        context.update(self.get_event_state_context_data(self.event))

        return context


class ServiceFeatureFlagMixin(OptionalBaseMixin):

    def pre_dispatch(self, request):
        response = super().pre_dispatch(request)
        features = self.event.feature_configuration

        if features.feature_services is False:
            raise PermissionDenied(self.get_permission_denied_message())
        return response


class ProductFeatureFlagMixin(OptionalBaseMixin):

    def pre_dispatch(self, request):
        response = super().pre_dispatch(request)
        features = self.event.feature_configuration

        if features.feature_products is False:
            raise PermissionDenied(self.get_permission_denied_message())
        return response


class EventOptionalMixin(OptionalBaseMixin):

    def get_context_data(self, **kwargs):
        # noinspection PyUnresolvedReferences
        context = super().get_context_data(**kwargs)
        context['themes'] = self.event.themes.all()
        return context
