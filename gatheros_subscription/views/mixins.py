from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import generic

from gatheros_event.helpers.event_business import is_paid_event
from gatheros_event.models import Event
from gatheros_event.views.mixins import AccountMixin, EventDraftStateMixin


class FeatureFlagMixinBaseMixin(AccountMixin, generic.View, EventDraftStateMixin):
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
        kwargs.update({'event': self.event})
        context.update(EventDraftStateMixin.get_context_data(self, **kwargs))
        context['event'] = self.event
        context['is_paid_event'] = is_paid_event(self.event)
        return context


class CheckinFeatureFlagMixin(FeatureFlagMixinBaseMixin):

    def pre_dispatch(self, request):
        response = super().pre_dispatch(request)
        features = self.event.feature_configuration

        if features.feature_checkin is False:
            raise PermissionDenied(self.get_permission_denied_message())
        return response


class SurveyFeatureFlagMixin(FeatureFlagMixinBaseMixin):

    def pre_dispatch(self, request):
        response = super().pre_dispatch(request)
        features = self.event.feature_configuration

        if features.feature_survey is False:
            if self.request.is_ajax():
                return HttpResponse(status=403)
            raise PermissionDenied(self.get_permission_denied_message())
        return response
