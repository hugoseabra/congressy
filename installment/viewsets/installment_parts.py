from rest_framework import permissions
from rest_framework.generics import ListAPIView

from installment.models import InstallmentPart, InstallmentContract
from installment.serializers import InstallmentPartSerializer


class PartsPermission(permissions.BasePermission):
    """
    Global permission check for blacklisted IPs.
    """

    def has_permission(self, request, view):
        user = request.user

        if not hasattr(user, 'person'):
            return False

        person = request.user.person

        participante_contracts = InstallmentContract.objects.filter(
            subscription__person_id=str(person.pk)
        )

        org_pks = [
            m.organization.pk
            for m in user.person.members.filter(active=True)
        ]

        organization_contracts = InstallmentContract.objects.filter(
            subscription__event__organization__in=org_pks
        )

        installment_contract_pk = request.query_params.get('pk')
        try:
            installment_contract = InstallmentContract.objects.get_queryset(
                pk=installment_contract_pk)
        except InstallmentContract.DoesNotExist:
            return False

        return installment_contract in participante_contracts or \
               installment_contract in organization_contracts


class InstallmentPartsList(ListAPIView):
    serializer_class = InstallmentPartSerializer
    permission_classes = (PartsPermission,)

    def get_queryset(self):
        installment_contract_pk = self.request.query_params.get('pk')
        return InstallmentPart.objects.filter(
            contract_pk=installment_contract_pk,
        )
