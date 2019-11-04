from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from gatheros_event.helpers.account import is_organization_member
from payment.serializers import (
    SubscriptionCheckoutSerializer,
    TransactionSerializer,
)
from .mixins import RestrictionViewMixin


class SubscriptionCheckoutView(RestrictionViewMixin, CreateAPIView):
    serializer_class = SubscriptionCheckoutSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        subscription = serializer.form_instance.subscription_instance
        person = subscription.person

        is_member = is_organization_member(request,
                                           subscription.event.organization)

        if person.user != self.request.user and is_member is False:
            return Response(
                {
                    'detail': 'unauthorized'
                },
                status=status.HTTP_401_UNAUTHORIZED, )

        transaction = serializer.save()

        new_serializer = TransactionSerializer(instance=transaction)
        headers = self.get_success_headers(new_serializer.data)
        return Response(new_serializer.data,
                        status=status.HTTP_201_CREATED,
                        headers=headers)
