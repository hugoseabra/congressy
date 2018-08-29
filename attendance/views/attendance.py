from gatheros_event.helpers import reports
from django.views import View, generic
from attendance.forms import AttendanceServiceForm
from attendance.models import AttendanceCategoryFilter, \
    AttendanceService, Checkin, Checkout
from gatheros_event.models import Event
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
        context['attendance_list'] = AttendanceService.objects.get(
            pk=self.kwargs.get('pk'))

        return context


class CheckinListView(generic.TemplateView):
    template_name = 'attendance/checkin-list.html'
    object = None

    def get_attendance_list(self):
        return AttendanceService.objects.get(pk=self.kwargs.get('pk'))

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_attendance_list()

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['attendance_list'] = self.get_attendance_list()
        context['event'] = Event.objects.get(pk=self.kwargs.get('event_pk'))
        context['attendances'] = self.get_attendances()

        return context

    def get_attendances(self):
        return Checkin.objects.filter(
            attendance_service=self.object,
            checkout__isnull=True
        ).order_by('-created_on')


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
        context = super().get_context_data(**kwargs)
        context['attendance_list'] = self.get_attendance_list()
        context['event'] = Event.objects.get(pk=self.kwargs.get('event_pk'))
        context.update({
            'attendances': self.get_attendances(),
            'search_by': self.search_by,
            'confirmed': self.get_number_confirmed(),
            'number_attendances': self.get_number_attendances(),
            'total_subscriptions': self.get_number_subscription(),
            'reports': self.get_report()
        })
        return context

    def get_attendances(self):
        try:
            list = Checkin.objects.filter(
                attendance_service=self.object,
                checkout__isnull=True
            ).order_by('-created_on')
            return list[0:5]

        except Subscription.DoesNotExist:
            return []

    def get_number_attendances(self):
        try:
            return Checkin.objects.filter(
                attendance_service=self.object,
                checkout__isnull=True
            ).order_by('-created_on').count()

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

        def perc(num, num_total):
            if num_total == 0:
                return 0
            return '{0:.2f}%'.format((num * 100) / num_total)

        queryset = Subscription.objects.filter(
            checkins__attendance_service__pk=self.get_attendance_list().pk)

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
