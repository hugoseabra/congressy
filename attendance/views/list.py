from django.views.generic import ListView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from gatheros_event.helpers.account import update_account
from attendance.models import AttendanceService
from django.shortcuts import redirect

from gatheros_event.models import Event
from gatheros_event.views.mixins import AccountMixin


class ManageListAttendanceView(AccountMixin, ListView):
    model = AttendanceService
    event = None
    template_name = 'attendance/manage-list-attendance.html'
    ordering = ['name']

    def pre_dispatch(self, request):
        try:
            self.event = Event.objects.get(pk=self.kwargs.get('event_pk'))

        except Event.DoesNotExist:
            messages.warning(
                request,
                "Evento não informado."
            )
            return redirect(reverse_lazy('event:event-list'))

        else:
            update_account(
                request=self.request,
                organization=self.event.organization,
                force=True
            )

    def get_queryset(self):
        query_set = super().get_queryset()
        return query_set.filter(event=self.event).order_by('pk')

    def can_access(self):
        return self.is_manager

    def get_context_data(self, **kwargs):
        # noinspection PyUnresolvedReferences
        context = super().get_context_data(**kwargs)
        context['event'] = self.event
        context['has_inside_bar'] = True
        context['active'] = 'attendance'
        context['attendance_lists'] = AttendanceService.objects.filter(event = self.event)
        return context
