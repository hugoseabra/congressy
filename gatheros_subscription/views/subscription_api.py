import re
from rest_framework import generics
from rest_framework.response import Response

from gatheros_subscription.models import Subscription
from gatheros_subscription.serializers import CheckInSubscriptionSerializer
from attendance.helpers.attendance import subscription_is_checked

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
        for item in response.data['results']:
            item['has_certificate'] = subscription_is_checked(item['pk'])

        return response

    def get_queryset(self) -> list:
        event_pk = self.kwargs.get('event_pk')
        if self.query is not None and self.query != '':

            # All subscriptions in the event
            queryset = Subscription.objects.filter(
                event=event_pk,
                completed=True,
                test_subscription=False,
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


class SubscriptionUpdateAttendedAPIView(generics.GenericAPIView):
    """
        API endpoint that allows Subscriptions to be viewed.
    """
    query = None

    serializer_class = CheckInSubscriptionSerializer
    lookup_url_kwarg = 'pk'

    def get_queryset(self):
        event_pk = self.kwargs.get('event_pk')
        queryset = Subscription.objects.filter(
            event=event_pk,
            completed=True,
        ).exclude(status=Subscription.CANCELED_STATUS)
        return queryset

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data,
                                         partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()
