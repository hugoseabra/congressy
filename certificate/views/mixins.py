from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import generic
from django.views.generic.base import ContextMixin

from gatheros_event.helpers.event_business import is_paid_event
from gatheros_event.models import Event
from gatheros_event.views.mixins import AccountMixin, EventDraftStateMixin


class CertificateBaseMixin(AccountMixin, generic.View, EventDraftStateMixin):
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


class CertificateFeatureFlagMixin(ContextMixin, CertificateBaseMixin):

    def can_access(self):
        can = super().can_access()
        if can is False:
            return False
        features = self.event.feature_configuration
        return features.feature_certificate is True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = self.event
        context['is_paid_event'] = is_paid_event(self.event)

        context.update(self.get_event_state_context_data(self.event))

        return context