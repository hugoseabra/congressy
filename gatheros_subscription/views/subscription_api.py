from rest_framework import viewsets

from gatheros_subscription.models import Subscription
from gatheros_subscription.serializers import CheckInSubscriptionSerializer
from rest_framework import generics


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
