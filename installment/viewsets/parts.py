from rest_framework import status, exceptions
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from installment.models import Part, Contract
from installment.serializers import PartSerializer
from .mixins import RestrictionViewMixin


class PartsList(RestrictionViewMixin, ListAPIView):
    serializer_class = PartSerializer

    def get_queryset(self):

        installment_contract_pk = self.kwargs.get('pk')
        assert installment_contract_pk is not None

        try:
            installment_contract = \
                Contract.objects.get(pk=installment_contract_pk)
        except Contract.DoesNotExist:
            return Part.objects.none()

        user = self.request.user

        if not hasattr(user, 'person'):
            return Part.objects.none()

        org_pks = [
            m.organization.pk
            for m in user.person.members.filter(active=True)
        ]

        organization_contracts = Contract.objects.filter(
            subscription__event__organization__in=org_pks
        )

        if installment_contract not in organization_contracts:
            return Part.objects.none()

        parts = Part.objects.filter(
            contract__pk=installment_contract_pk,
        )

        return parts


class PartViewSet(RestrictionViewMixin, ModelViewSet):
    serializer_class = PartSerializer

    def get_queryset(self):
        installment_contract_pk = self.request.query_params.get('pk')
        return Part.objects.filter(
            contract_pk=installment_contract_pk,
        )

    def get_object(self):
        obj = super().get_object()
        user = self.request.user
        if not hasattr(user, 'person'):
            raise exceptions.PermissionDenied()

        person = user.person

        participante_contracts = Contract.objects.filter(
            subscription__person_id=str(person.pk)
        )

        org_pks = [
            m.organization.pk
            for m in user.person.members.filter(active=True)
        ]

        organization_contracts = Contract.objects.filter(
            subscription__event__organization__in=org_pks
        )

        if obj.contract not in participante_contracts and obj.contract not \
                in organization_contracts:
            raise exceptions.PermissionDenied()

        return obj

    def list(self, request, *args, **kwargs):
        content = {
            'detail': 'method not allowed'
        }

        return Response(content, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, *args, **kwargs):
        content = {
            'detail': 'method not allowed'
        }

        return Response(content, status=status.HTTP_405_METHOD_NOT_ALLOWED)
