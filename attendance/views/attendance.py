from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect

from django.views import View, generic
from attendance.forms import AttendanceServiceForm
from attendance.models import AttendanceCategoryFilter, Attendance, AttendanceService
from gatheros_event.models import Event
from gatheros_event.views.mixins import AccountMixin
from gatheros_event.helpers.account import update_account
from gatheros_subscription.models import Subscription


class AttendanceSearchView(generic.FormView):
    form_class = AttendanceServiceForm
    http_method_names = ['post']
    search_by = 'name'
    register_type = None
    attendance_list = None
    event = None
    subscription = None
    user = None

    def get_event(self):
        return Event.objects.get(pk=self.kwargs.get('event_pk'))

    def get_subscription(self):
        return Subscription.objects.get(pk=self.kwargs.get('subscription_pk'))

    def get_attendance_list(self):
        return AttendanceService.objects.get(pk=self.kwargs.get('pk'))

    def dispatch(self, request, *args, **kwargs):
        self.event = self.get_event()
        self.attendance_list = self.get_attendance_list()
        self.subscription = self.get_subscription()
        self.user = request.user.id

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        url = reverse(
            'attendance:attendance',
            kwargs={'event_pk': self.kwargs.get('event_pk'),
                    'subscription_pk': self.kwargs.get('subscription_pk'),
                    'pk': self.kwargs.get('pk')}
        )
        if self.search_by is not None and self.search_by != 'name':
            url += '?search_by=' + str(self.search_by)

        return url

    def get_permission_denied_url(self):
        return self.get_success_url()

    def get_form_kwargs(self):
        kwargs = super(AttendanceSearchView, self).get_form_kwargs()
        kwargs.update({'subscription': self.get_subscription(),
                       'attendance_service': self.get_attendance_list(),
                       'attended_by' : self.user})
        return kwargs

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return super(AttendanceSearchView, self).form_invalid(form)

    def form_valid(self, form):
        sub = self.get_subscription()

        try:
            if self.register_type is None:
                raise Exception('Nenhuma ação foi informada.')

            register_name = 'Credenciamento' \
                if self.register_type == 'register' \
                else 'Cancelamento de credenciamento'

        except Exception as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)

        else:
            messages.success(
                self.request,
                '{} de `{}` registrado com sucesso.'.format(
                    register_name,
                    sub.person.name
                )
            )
            form.attended(self.register_type == 'register')
            return super(AttendanceSearchView, self).form_valid(form)

    def post(self, request, *args, **kwargs):
        self.search_by = request.POST.get('search_by')
        self.register_type = request.POST.get('action')

        return super(AttendanceSearchView, self).post(
            request,
            *args,
            **kwargs
        )


class SubscriptionAttendanceSearchView(generic.TemplateView):
    template_name = 'subscription/attendance.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['has_inside_bar'] = True
        context['active'] = 'checkin'
        return context


class SubscriptionAttendanceListView(generic.TemplateView):
    template_name = 'subscription/attendance-list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['attendances'] = self.get_attendances()
        context['has_inside_bar'] = True
        context['active'] = 'checkin-list'
        return context

    def get_attendances(self):
        return Attendance.objects.filter(
            operation='check-in',
            attendence_service=True,
            event=self.get_event(),
        ).exclude(status=Subscription.CANCELED_STATUS).order_by('-attended_on')