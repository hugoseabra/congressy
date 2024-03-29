from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.viewsets import AuthenticatedViewSetMixin
from installment.models import Contract
from installment.serializers import ContractSerializer


class ContractViewSet(AuthenticatedViewSetMixin, ModelViewSet):
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

        if 'status' in self.request.query_params:
            statuses = self.request.query_params.get('status').split(',')
            return qs.filter(status__in=statuses)

        return qs

    def destroy(self, request, *args, **kwargs):
        content = {
            'detail': 'method not allowed'
        }

        return Response(content, status=status.HTTP_405_METHOD_NOT_ALLOWED)
