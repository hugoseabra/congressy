from rest_framework import viewsets
from rest_framework.authentication import (
    BasicAuthentication,
    SessionAuthentication,
)
from rest_framework.permissions import IsAuthenticated

from attendance import models, serializers


class RestrictionViewMixin(object):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)


class AttendanceServiceViewSet(RestrictionViewMixin, viewsets.ModelViewSet):
    """
         Essa view é responsavel por retornar o usuário, se membro da
         organização, poderá acessar os serviços opcionais de todos os seus
         eventos
    """
    queryset = models.AttendanceService.objects.all().order_by('name')
    serializer_class = serializers.AttendanceServiceSerializer

    def get_queryset(self):
        user = self.request.user

        org_pks = [
            m.organization.pk
            for m in user.person.members.filter(active=True)
        ]

        queryset = super().get_queryset()
        return queryset.filter(event__organization_id__in=org_pks)


class CheckinViewSet(RestrictionViewMixin, viewsets.ModelViewSet):
    queryset = models.Checkin.objects.all()
    serializer_class = serializers.CheckinSerializer

    def get_queryset(self):
        user = self.request.user

        org_pks = [
            m.organization.pk
            for m in user.person.members.filter(active=True)
        ]

        queryset = super().get_queryset()
        return queryset.filter(
            attendance_service__event__organization_id__in=org_pks
        )


class CheckoutViewSet(RestrictionViewMixin, viewsets.ModelViewSet):
    queryset = models.Checkout.objects.all()
    serializer_class = serializers.CheckoutSerializer

    def get_queryset(self):
        user = self.request.user

        org_pks = [
            m.organization.pk
            for m in user.person.members.filter(active=True)
        ]

        queryset = super().get_queryset()
        return queryset.filter(
            attendance_service__event__organization_id__in=org_pks
        )
