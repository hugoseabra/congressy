from rest_framework.viewsets import ModelViewSet

from installment.models import InstallmentContract
from installment.serializers import InstallmentContractSerializer
from .mixins import RestrictionViewMixin


class InstallmentContractViewSet(RestrictionViewMixin, ModelViewSet):
    serializer_class = InstallmentContractSerializer

    def get_queryset(self):

        user = self.request.user

        if 'mode' in self.request.query_params:
            mode = self.request.query_params.get('mode')

            if mode == 'organizer':
                org_pks = [
                    m.organization.pk
                    for m in user.person.members.filter(active=True)
                ]

                return InstallmentContract.objects.filter(
                    subscription__event__organization__in=org_pks
                )

        if not hasattr(user, 'person'):
            return InstallmentContract.objects.get_queryset()

        person = self.request.user.person

        return InstallmentContract.objects.filter(
            subscription__person_id=str(person.pk)
        )
