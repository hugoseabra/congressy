import re
from rest_framework import generics
from rest_framework.response import Response

from gatheros_subscription.models import Subscription
from attendance.models import AttendanceService, AttendanceCategoryFilter
from gatheros_subscription.serializers import CheckInSubscriptionSerializer


class SubscriptionSearchViewSet(generics.ListAPIView):
    """
        API endpoint that allows Subscriptions to be viewed.
    """
    query = None

    serializer_class = CheckInSubscriptionSerializer

    def get(self, request, *args, **kwargs):
        if 'query' in request.GET:
            self.query = request.GET.get('query')

        response = super().get(request, *args, **kwargs)
        return response

    def get_queryset(self) -> list:
        event_pk = self.kwargs.get('event_pk')
        attendance_service_pk = self.kwargs.get('pk')
        cat_filter_qs = AttendanceCategoryFilter.objects.get_queryset()

        lot_category_pks = [
            service.lot_category.pk
            for service in cat_filter_qs.filter(
                attendance_service__pk=attendance_service_pk
            )
        ]

        if self.query is not None and self.query != '':

            # All subscriptions in the event
            queryset = Subscription.objects.filter(
                event=event_pk,
                completed=True,
                test_subscription=False,
                lot__category_id__in=lot_category_pks
            )

            # Fetch by event code
            if self.query.isdigit():
                try:
                    event_count = int(self.query)
                    return [queryset.get(event_count=event_count)]
                except Subscription.DoesNotExist:
                    pass

            # Filter by name
            name_query = queryset.filter(person__name__icontains=self.query)
            if name_query.count() > 0:
                return name_query[:15]

            # Filter by email
            email_query = queryset.filter(person__email__icontains=self.query)
            if email_query.count() > 0:
                return email_query[:15]

            # Fetch by subscription code
            try:
                return [queryset.get(code=self.query.upper())]
            except Subscription.DoesNotExist:
                pass

            query = re.sub('\.', '', self.query)
            query = re.sub('/', '', query)
            query = re.sub('-', '', query)

            cpf_query = queryset.filter(person__cpf=query)
            if cpf_query.count() > 0:
                return cpf_query[:15]

            cnpf_query = queryset.filter(person__institution_cnpj=query)
            if cnpf_query.count() > 0:
                return cnpf_query[:15]

        return []

