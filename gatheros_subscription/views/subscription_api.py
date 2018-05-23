from rest_framework import generics
from rest_framework.response import Response

from gatheros_subscription.models import Subscription
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

    def get_queryset(self):
        event_pk = self.kwargs.get('event_pk')
        if self.query is not None:
            queryset = Subscription.objects.filter(event=event_pk)
            name_query = queryset.filter(person__name__icontains=self.query)
            if name_query.count() > 0:
                return name_query[:15]

            email_query = queryset.filter(person__email__icontains=self.query)
            if email_query.count() > 0:
                return email_query[:15]

            try:
                return [queryset.get(code=self.query.upper())]
            except Subscription.DoesNotExist:
                pass

            try:
                return [queryset.get(person__cpf=self.query)]
            except Subscription.DoesNotExist:
                pass

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
        queryset = Subscription.objects.filter(event=event_pk)
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
