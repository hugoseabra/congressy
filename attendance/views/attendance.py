from django.shortcuts import redirect, reverse
from django.views import generic

from attendance.models import (
    AttendanceCategoryFilter,
    AttendanceService,
    Checkin,
)
from gatheros_event.helpers import reports
from gatheros_event.models import Event
from gatheros_subscription.models import Subscription
from .mixins import AttendanceFeatureFlagMixin


class AttendancePageSearchView(AttendanceFeatureFlagMixin,
                               generic.TemplateView):
    template_name = 'attendance/attendance.html'
    types_accepted = ['typing', 'barcode', None]

    def __init__(self, **initargs):
        self.lot_categories = None
        super().__init__(**initargs)

    def can_access(self):
        can = super().can_access()
        if can is False:
            return False

        self.permission_denied_url = reverse(
            'event:event-panel',
            kwargs={
                'pk': self.event.pk,
            }
        )
        search_type = self.request.GET.get('search_type')
        return search_type in self.types_accepted

    def get_lot_categories(self):
        if self.lot_categories:
            return self.lot_categories

        items = []
        lc_filter_pks = []
        for item in AttendanceCategoryFilter.objects.filter(
                attendance_service_id=self.object.pk):
            lc_filter_pks.append(item.lot_category_id)

        for lc in self.event.lot_categories.all().order_by('name'):
            if lc.id in lc_filter_pks:
                items.append(lc.name)

        self.lot_categories = items

        return items

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = self.event
        context['object'] = self.object
        context['lot_categories'] = self.get_lot_categories()
        context['search_type'] = self.request.GET.get('search_type')
        return context


class CheckinListView(AttendanceFeatureFlagMixin, generic.TemplateView):
    template_name = 'attendance/checkin-list.html'
    object = None

    def __init__(self, **initargs):
        self.attendances = []
        super().__init__(**initargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = self.event
        context['object'] = self.object
        context['attendances'] = self.get_attendances()

        return context

    def get_attendances(self):
        if self.attendances:
            return self.attendances

        self.attendances = Checkin.objects.filter(
            attendance_service=self.object,
            checkout__isnull=True
        ).order_by('-created_on')
        return self.attendances


class AttendanceDashboardView(AttendanceFeatureFlagMixin, generic.DetailView):
    model = AttendanceService
    template_name = 'attendance/attendance-dashboard.html'
    search_by = 'name'

    def __init__(self, **initargs):
        self.attendances = []
        self.category_ids = []
        super().__init__(**initargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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
        if self.attendances:
            return self.attendances[0:5]

        self.attendances = Checkin.objects.filter(
            attendance_service=self.object,
            checkout__isnull=True
        ).order_by('-created_on')

        return self.attendances[0:5]

    def get_category_filter(self):
        if self.category_ids:
            return self.category_ids

        self.category_ids = []
        all_category = AttendanceCategoryFilter.objects.filter(
            attendance_service=self.object
        ).values('lot_category_id')

        all_category = list(list(all_category))
        for category in all_category:
            self.category_ids.append(category['lot_category_id'])

        return self.category_ids

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
                event=self.event,
                completed=True, test_subscription=False,
                lot__category_id__in=self.get_category_filter()
            ).exclude(status=Subscription.CANCELED_STATUS).count()

        return total

    def get_number_confirmed(self):

        confirmed = \
            Subscription.objects.filter(
                status=Subscription.CONFIRMED_STATUS,
                completed=True, test_subscription=False,
                event=self.event,
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
            status=Subscription.CONFIRMED_STATUS,
            completed=True, test_subscription=False,
            event=self.event
        )

        queryset = queryset.filter(
            checkins__attendance_service__pk=self.object.pk,
            checkins__checkout__isnull=True,
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
