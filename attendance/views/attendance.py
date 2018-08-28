from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect
from gatheros_event.helpers import reports
from django.views import View, generic
from attendance.forms import AttendanceServiceForm
from attendance.models import AttendanceCategoryFilter, \
    AttendanceService
from gatheros_event.models import Event
from gatheros_event.views.mixins import AccountMixin
from gatheros_event.helpers.account import update_account
from gatheros_subscription.models import Subscription


# class AttendanceSearchView(generic.FormView):
#     form_class = AttendanceServiceForm
#     http_method_names = ['post']
#     search_by = 'name'
#     register_type = None
#     attendance_list = None
#     event = None
#     subscription = None
#     user = None
#
#     def get_event(self):
#         return Event.objects.get(pk=self.kwargs.get('event_pk'))
#
#     def get_subscription(self):
#         return Subscription.objects.get(pk=self.kwargs.get('subscription_pk'))
#
#     def get_attendance_list(self):
#         return AttendanceService.objects.get(pk=self.kwargs.get('pk'))
#
#     def dispatch(self, request, *args, **kwargs):
#         self.event = self.get_event()
#         self.attendance_list = self.get_attendance_list()
#         self.subscription = self.get_subscription()
#         self.user = request.user.id
#
#         return super().dispatch(request, *args, **kwargs)
#
#     def get_success_url(self):
#         url = reverse(
#             'attendance:attendance',
#             kwargs={'event_pk': self.kwargs.get('event_pk'),
#                     'subscription_pk': self.kwargs.get('subscription_pk'),
#                     'pk': self.kwargs.get('pk')}
#         )
#         if self.search_by is not None and self.search_by != 'name':
#             url += '?search_by=' + str(self.search_by)
#
#         return url
#
#     def get_permission_denied_url(self):
#         return self.get_success_url()
#
#     def get_form_kwargs(self):
#         kwargs = super(AttendanceSearchView, self).get_form_kwargs()
#         kwargs.update({'subscription': self.get_subscription(),
#                        'attendance_service': self.get_attendance_list(),
#                        'attended_by': self.user})
#         return kwargs
#
#     def form_invalid(self, form):
#         messages.error(self.request, form.errors)
#         return super(AttendanceSearchView, self).form_invalid(form)
#
#     def form_valid(self, form):
#         sub = self.get_subscription()
#
#         try:
#             if self.register_type is None:
#                 raise Exception('Nenhuma ação foi informada.')
#
#             register_name = 'Credenciamento' \
#                 if self.register_type == 'register' \
#                 else 'Cancelamento de credenciamento'
#
#         except Exception as e:
#             form.add_error(None, str(e))
#             return self.form_invalid(form)
#
#         else:
#             messages.success(
#                 self.request,
#                 '{} de `{}` registrado com sucesso.'.format(
#                     register_name,
#                     sub.person.name
#                 )
#             )
#             form.attended(self.register_type == 'register')
#             return super(AttendanceSearchView, self).form_valid(form)
#
#     def post(self, request, *args, **kwargs):
#         self.search_by = request.POST.get('search_by')
#         self.register_type = request.POST.get('action')
#
#         return super(AttendanceSearchView, self).post(
#             request,
#             *args,
#             **kwargs
#         )


class AttendancePageSearchView(generic.TemplateView):
    template_name = 'attendance/attendance.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = Event.objects.get(pk=self.kwargs.get('event_pk'))
        context['attendance_list'] = AttendanceService.objects.get(pk=self.kwargs.get('pk'))
        return context


class SubscriptionAttendanceListView(generic.TemplateView):
    template_name = 'attendance/attendance-list.html'
    object = None

    def get_attendance_list(self):
        return AttendanceService.objects.get(pk=self.kwargs.get('pk'))

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_attendance_list()

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['attendances'] = self.get_attendances()
        context['has_inside_bar'] = True
        context['active'] = 'checkin-list'
        return context

    def get_attendances(self):
        return Attendance.objects.filter(
            attendence_service=self.object,
            subscription__attended=True,
            checkout_on=None
        ).exclude(Attendance.objects.filter(
            subscription__status=Subscription.CANCELED_STATUS,
            checkin_on=None
        )).order_by('-checkin_on')

    class AttendanceDashboardView(generic.TemplateView):
        template_name = 'attendance/attendance-dashboard.html'
        search_by = 'name'
        object = None

        def get_event(self):
            return Event.objects.get(pk=self.kwargs.get('event_pk'))

        def get_attendance_list(self):
            return AttendanceService.objects.get(pk=self.kwargs.get('pk'))

        def dispatch(self, request, *args, **kwargs):
            self.object = self.get_attendance_list()

            return super().dispatch(request, *args, **kwargs)

        def get_context_data(self, **kwargs):
            cxt = super().get_context_data(**kwargs)
            cxt.update({
                'attendances': self.get_attendances(),
                'search_by': self.search_by,
                'has_inside_bar': True,
                'active': 'checkin-dashboard',
                'confirmed': self.get_number_confirmed(),
                'number_attendances': self.get_number_attendances(),
                'total_subscriptions': self.get_number_subscription(),
                'reports': self.get_report()
            })
            return cxt

        def get_attendances(self):
            try:
                list = Attendance.objects.filter(
                    attendence_service=self.object,
                    subscription__attended=True,
                    checkout_on=None
                ).exclude(Attendance.objects.filter(
                    subscription__status=Subscription.CANCELED_STATUS,
                    checkin_on=None
                )).order_by('-checkin_on')
                return list[0:5]

            except Subscription.DoesNotExist:
                return []

        def get_number_attendances(self):
            try:
                return Attendance.objects.filter(
                    attendence_service=self.object,
                    subscription__attended=True,
                    checkout_on=None
                ).exclude(Attendance.objects.filter(
                    subscription__status=Subscription.CANCELED_STATUS,
                    checkin_on=None
                )).count()

            except Subscription.DoesNotExist:
                return 0

        def get_number_subscription(self):

            total = \
                Subscription.objects.filter(
                    event=self.get_event(),
                    completed=True, test_subscription=False
                ).exclude(status=Subscription.CANCELED_STATUS).count()

            return total

        def get_number_confirmed(self):

            confirmed = \
                Subscription.objects.filter(
                    status=Subscription.CONFIRMED_STATUS,
                    completed=True, test_subscription=False,
                    event=self.get_event()
                ).count()

            return confirmed

        def get_report(self):
            """
            Recupera um dicinário com informaçõse que podem ser utilizadas como
            relatório.
            """
            if not hasattr(self, 'subscriptions'):
                return {}

            def perc(num, num_total):
                if num_total == 0:
                    return 0
                return '{0:.2f}%'.format((num * 100) / num_total)

            queryset = Subscription.objects.filter(
                attendances__attendance_service__pk=self.get_attendance_list())

            total = queryset.count()

            reports_dict = {}

            gender_report = reports.get_report_gender(queryset)

            reports_dict.update(gender_report)
            reports_dict.update({
                'num_men': '{} ({})'.format(
                    gender_report['men'],
                    perc(gender_report['men'], total)
                ),
                'num_women': '{} ({})'.format(
                    gender_report['women'],
                    perc(gender_report['women'], total)
                ),
            })

            reports_dict.update(
                {'num_pnes': reports.get_report_gender(queryset)})
            reports_dict.update({
                'cities': reports.get_report_cities(queryset)
            })
            reports_dict.update({
                'ages': reports.get_report_age(queryset)
            })

            return reports_dict
