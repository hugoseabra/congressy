from rest_framework import viewsets
from rest_framework.authentication import (
    BasicAuthentication,
    SessionAuthentication,
)
from rest_framework.permissions import IsAuthenticated

from addon import models, serializers
from gatheros_event.models import Member


class RestrictionViewMixin(object):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)


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
            for m in user.person.members.filter(
                active=True,
                group=Member.ADMIN
            )
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
            for m in user.person.members.filter(
                active=True,
                group=Member.ADMIN
            )
        ]

        queryset = super().get_queryset()
        return queryset.filter(lot_category__event__organization__in=org_pks)


# class SubscriptionProductViewSet(viewsets.ModelViewSet):
#     """
#         API endpoint that allows users to be viewed or edited.
#     """
#     queryset = models.SubscriptionProduct.objects.all()
#     serializer_class = serializers.SubscriptionProductSerializer
#


# class SubscriptionServiceViewSet(viewsets.ModelViewSet):
#     """
#         API endpoint that allows users to be viewed or edited.
#     """
#     queryset = models.SubscriptionService.objects.all()
#     serializer_class = serializers.SubscriptionServiceSerializer
