from rest_framework import viewsets
from rest_framework.authentication import (
    BasicAuthentication,
    SessionAuthentication,
)
from rest_framework.permissions import IsAuthenticated
from .addons_api_permissions import IsNotFreeEvent

from addon import models, serializers


class RestrictionViewMixin(object):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated, IsNotFreeEvent)


class ServiceViewSet(RestrictionViewMixin, viewsets.ModelViewSet):
    """
         Essa view é responsavel por retornar o usuário, se membro da
         organização, poderá acessar os serviços opcionais de todos os seus
         eventos
    """
    queryset = models.Service.objects.all().order_by('name')
    serializer_class = serializers.ServiceSerializer

    def get_queryset(self):
        user = self.request.user

        org_pks = [
            m.organization.pk
            for m in user.person.members.filter(active=True)
        ]

        queryset = super().get_queryset()
        return queryset.filter(lot_category__event__organization__in=org_pks)


class ProductViewSet(RestrictionViewMixin, viewsets.ModelViewSet):
    """
         Essa view é responsavel por retornar o usuário, se membro da
         organização, poderá acessar os produtos opcionais de todos os seus
         eventos
    """
    queryset = models.Product.objects.all().order_by('name')
    serializer_class = serializers.ProductSerializer

    def get_queryset(self):
        user = self.request.user

        org_pks = [
            m.organization.pk
            for m in user.person.members.filter(active=True)
        ]

        queryset = super().get_queryset()
        return queryset.filter(lot_category__event__organization__in=org_pks)


class SubscriptionServiceViewSet(RestrictionViewMixin, viewsets.ModelViewSet):
    """
         Essa view é responsavel por retornar
    """
    queryset = models.SubscriptionService.objects.all()
    serializer_class = serializers.SubscriptionServiceSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(subscription=self.kwargs.get('subscription_pk'))


class SubscriptionProductViewSet(RestrictionViewMixin, viewsets.ModelViewSet):
    """
         Essa view é responsavel por retornar
    """
    queryset = models.SubscriptionProduct.objects.all()
    serializer_class = serializers.SubscriptionProductSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(subscription=self.kwargs.get('subscription_pk'))
