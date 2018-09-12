from gatheros_event.helpers import reports
from django.views import View, generic
from attendance.forms import AttendanceServiceForm
from attendance.models import AttendanceCategoryFilter, \
    AttendanceService, Checkin, Checkout
from gatheros_event.models import Event
from gatheros_subscription.models import Subscription
from django.shortcuts import redirect

class AttendancePageSearchView(generic.TemplateView):
    template_name = 'attendance/attendance.html'
    object = None
    event = None
    search_type = None
    types_accepted = ['typing', 'qrcode', 'barcode', None]

    def dispatch(self, request, *args, **kwargs):
        self.object = AttendanceService.objects.get(pk=self.kwargs.get('pk'))
        self.event = Event.objects.get(pk=self.kwargs.get('event_pk'))
        search_type = request.GET.get('search_type')
        if search_type not in self.types_accepted:
            return redirect("attendance:attendance", event_pk=self.event.pk,
                            pk=self.object.pk)
        else:
            self.search_type = search_type
        return super().dispatch(request, *args, **kwargs)

    def get_lot_categories(self):
        items = []
        lc_filter_pks = []
        for item in AttendanceCategoryFilter.objects.filter(
                attendance_service_id=self.object.pk):
            lc_filter_pks.append(item.lot_category_id)

        for lc in self.event.lot_categories.all().order_by('name'):
            if lc.id in lc_filter_pks:
                items.append(lc.name)
        return items

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = self.event
        context['object'] = self.object
        context['attendance_list'] = AttendanceService.objects.get(
            pk=self.kwargs.get('pk'))
        context['lot_categories'] = self.get_lot_categories()
        context['search_type'] = self.search_type
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
        context['object'] = self.object
        context['attendances'] = self.get_attendances()

        return context

    def get_attendances(self):
        return Checkin.objects.filter(
            attendance_service=self.object,
            checkout__isnull=True
        ).order_by('-created_on')


class AttendanceDashboardView(generic.DetailView):
    model = AttendanceService
    template_name = 'attendance/attendance-dashboard.html'
    search_by = 'name'
    event = None

    def get_event(self):
        return Event.objects.get(pk=self.kwargs.get('event_pk'))

    def get_attendance_list(self):
        return AttendanceService.objects.get(pk=self.kwargs.get('pk'))

    def dispatch(self, request, *args, **kwargs):
        self.event = Event.objects.get(pk=self.kwargs.get('event_pk'))

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['attendance_list'] = self.get_attendance_list()
        context['event'] = self.event
        context['object'] = self.object
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
        list = Checkin.objects.filter(
            attendance_service=self.object,
            checkout__isnull=True
        ).order_by('-created_on')
        return list[0:5]

    def get_category_filter(self):
        category_id = []
        all_category = AttendanceCategoryFilter.objects.filter(
            attendance_service=self.get_attendance_list()
        ).values('lot_category_id')
        all_category = list(list(all_category))
        for category in all_category:
            category_id.append(category['lot_category_id'])

        return category_id


    def get_number_attendances(self):
        queryset = Subscription.objects.filter(
            status=Subscription.CONFIRMED_STATUS,
            completed=True, test_subscription=False,
            event=self.event
        )

        queryset = queryset.filter(
            checkins__attendance_service__pk=self.object.pk,
            checkins__checkout__isnull=True,
        )

        return queryset.count()


    def get_number_subscription(self):

        total = \
            Subscription.objects.filter(
                event=self.get_event(),
                completed=True, test_subscription=False,
                lot__category_id__in=self.get_category_filter()
            ).exclude(status=Subscription.CANCELED_STATUS).count()

        return total

    def get_number_confirmed(self):

        confirmed = \
            Subscription.objects.filter(
                status=Subscription.CONFIRMED_STATUS,
                completed=True, test_subscription=False,
                event=self.get_event(),
                lot__category_id__in=self.get_category_filter()
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

        queryset = queryset.filter(
            checkins__isnull=False,
            checkins__checkout__isnull=True
        )

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
