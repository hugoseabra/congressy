from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from installment.models import Contract
from installment.serializers import ContractSerializer
from .mixins import RestrictionViewMixin


class ContractViewSet(RestrictionViewMixin, ModelViewSet):
    serializer_class = ContractSerializer

    def get_queryset(self):
        user = self.request.user

        org_pks = [
            m.organization.pk
            for m in user.person.members.filter(active=True)
        ]

        qs = Contract.objects.filter(
            subscription__event__organization__in=org_pks
        )

        if 'subscription' in self.request.query_params:
            subscription_pk = self.request.query_params.get('subscription')
            return qs.filter(subscription_id=subscription_pk)

        if 'event' in self.request.query_params:
            event_pk = self.request.query_params.get('event')
            return qs.filter(subscription__event_id=event_pk)

        return qs

    def destroy(self, request, *args, **kwargs):
        content = {
            'detail': 'method not allowed'
        }

        return Response(content, status=status.HTTP_405_METHOD_NOT_ALLOWED)
