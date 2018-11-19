from rest_framework import status, exceptions
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from installment.models import InstallmentPart, InstallmentContract
from installment.serializers import InstallmentPartSerializer
from .mixins import RestrictionViewMixin


class InstallmentPartsList(RestrictionViewMixin, ListAPIView):
    serializer_class = InstallmentPartSerializer

    def get_queryset(self):

        installment_contract_pk = self.kwargs.get('pk')
        assert installment_contract_pk is not None

        parts = InstallmentPart.objects.filter(
            contract__pk=installment_contract_pk,
        )

        try:
            installment_contract = \
                InstallmentContract.objects.get(pk=installment_contract_pk)
        except InstallmentContract.DoesNotExist:
            return InstallmentPart.objects.none()

        user = self.request.user

        if not hasattr(user, 'person'):
            return InstallmentPart.objects.none()

        person = user.person

        participante_contracts = InstallmentContract.objects.filter(
            subscription__person_id=str(person.pk)
        )

        if installment_contract in participante_contracts:
            return parts

        org_pks = [
            m.organization.pk
            for m in user.person.members.filter(active=True)
        ]

        organization_contracts = InstallmentContract.objects.filter(
            subscription__event__organization__in=org_pks
        )

        if installment_contract not in organization_contracts:
            return InstallmentPart.objects.none()

        return parts


class InstallmentPartViewSet(RestrictionViewMixin, ModelViewSet):
    serializer_class = InstallmentPartSerializer

    def list(self, request, *args, **kwargs):
        content = {
            'detail': 'method not allowed'
        }

        return Response(content, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def get_queryset(self):
        installment_contract_pk = self.request.query_params.get('pk')
        return InstallmentPart.objects.filter(
            contract_pk=installment_contract_pk,
        )

    def get_object(self):
        obj = super().get_object()
        user = self.request.user
        if not hasattr(user, 'person'):
            raise exceptions.PermissionDenied()

        person = user.person

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

        if obj.contract not in participante_contracts and obj.contract not \
                in organization_contracts:
            raise exceptions.PermissionDenied()

        return obj
