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

        if 'event' in self.request.query_params:
            event_pk = self.request.query_params.get('event')
            return qs.filter(subscription__event_id=event_pk)

        return qs
