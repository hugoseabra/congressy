from typing import Any

from rest_framework import viewsets, status
from rest_framework.authentication import (
    BasicAuthentication,
    SessionAuthentication,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from addon import models, serializers


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
            for m in user.person.members.filter(active=True)
        ]

        queryset = super().get_queryset()
        return queryset.filter(
            lot_category__event__organization_id__in=org_pks
        )

    def list(self, request, *args, **kwargs):
        event_pk = request.query_params.get('event', None)

        if event_pk is None:
            content = {
                'errors': ['missing event in query string', ]
            }

            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        try:
            event_pk = int(event_pk)
        except ValueError:
            content = {
                'errors': [
                    "event in query string is not int: '{}' ".format(event_pk),
                ]
            }

            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        queryset = self.get_queryset()
        queryset = queryset.filter(lot_category__event_id=event_pk)

        page = self.paginate_queryset(self.filter_queryset(queryset))
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


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
        return queryset.filter(
            lot_category__event__organization_id__in=org_pks
        )

    def list(self, request, *args, **kwargs):
        event_pk = request.query_params.get('event', None)

        if event_pk is None:
            content = {
                'errors': ['missing event in query string', ]
            }

            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        try:
            event_pk = int(event_pk)
        except ValueError:
            content = {
                'errors': [
                    "event in query string is not int: '{}' ".format(event_pk),
                ]
            }

            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        queryset = self.get_queryset()
        queryset = queryset.filter(lot_category__event_id=event_pk)

        page = self.paginate_queryset(self.filter_queryset(queryset))
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class SubscriptionServiceViewSet(RestrictionViewMixin, viewsets.ModelViewSet):
    """
         Essa view é responsavel por retornar
    """
    queryset = models.SubscriptionService.objects.all()
    serializer_class = serializers.SubscriptionServiceSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(
            subscription_id=self.kwargs.get('subscription_pk')
        )


class SubscriptionProductViewSet(RestrictionViewMixin, viewsets.ModelViewSet):
    """
         Essa view é responsavel por retornar
    """
    queryset = models.SubscriptionProduct.objects.all()
    serializer_class = serializers.SubscriptionProductSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(
            subscription_id=self.kwargs.get('subscription_pk')
        )
