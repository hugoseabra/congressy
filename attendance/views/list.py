from django.views.generic import ListView

from attendance.models import AttendanceService, Checkin
from .mixins import AttendancesFeatureFlagMixin


class ManageListAttendanceView(AttendancesFeatureFlagMixin, ListView):
    model = AttendanceService
    template_name = 'attendance/manage-list-attendance.html'
    ordering = ['name']

    def get_queryset(self):
        query_set = super().get_queryset()
        return query_set.filter(event=self.event).order_by('pk')

    def get_context_data(self, **kwargs):
        # noinspection PyUnresolvedReferences
        context = super().get_context_data(**kwargs)
        context['event'] = self.event
        context['has_inside_bar'] = True
        context['active'] = 'attendance'
        context['is_staff'] = self.request.user.is_staff
        context['num_checkins'] = self.get_num_checkins()
        context['attendance_lists'] = AttendanceService.objects.filter(
            event=self.event
        )
        context.update(self.get_event_state_context_data(self.event))
        return context

    def get_num_checkins(self):
        checkins_qs = Checkin.objects.filter(
            attendance_service__event_id=self.event.pk,
            checkout__isnull=True,
        )
        return checkins_qs.count()
