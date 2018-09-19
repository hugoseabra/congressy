from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import generic

from attendance.models import AttendanceService
from gatheros_event.helpers.account import update_account
from gatheros_event.models import Event
from gatheros_event.views.mixins import AccountMixin, EventDraftStateMixin


class AttendanceBaseMixin(AccountMixin, generic.View, EventDraftStateMixin):
    permission_denied_message = 'Você não pode realizar esta ação.'

    def __init__(self, **initargs):
        self.event = None
        super().__init__(**initargs)

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

        update_account(
            request=self.request,
            organization=self.event.organization,
            force=True
        )

        return super().pre_dispatch(request)

    def get_context_data(self, **kwargs):
        # noinspection PyUnresolvedReferences
        context = super().get_context_data(**kwargs)

        context['event'] = self.event

        context.update(self.get_event_state_context_data(self.event))

        return context


class AttendancesFeatureFlagMixin(AttendanceBaseMixin):
    def can_access(self):
        features = self.event.feature_configuration
        return features.feature_checkin is True


class AttendanceFeatureFlagMixin(AttendancesFeatureFlagMixin):
    def __init__(self, **initargs):
        self.object = None
        super().__init__(**initargs)

    def pre_dispatch(self, request):
        super().pre_dispatch(request)
        self.object = AttendanceService.objects.get(pk=self.kwargs.get('pk'))

    def can_access(self):
        features = self.event.feature_configuration
        return features.feature_checkin is True
