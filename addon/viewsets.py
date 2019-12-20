import uuid
from typing import Any

from django.db.models import QuerySet
from rest_framework import viewsets, status
from rest_framework.response import Response

from addon import models, serializers
from core.viewsets import (
    AuthenticatedViewSetMixin,
    AuthenticatedOrReadOnlyViewSetMixin,
)
from gatheros_subscription.models import Subscription


class ServiceViewSet(AuthenticatedOrReadOnlyViewSetMixin,
                     viewsets.ModelViewSet):
    """
         Essa view é responsavel por retornar o usuário, se membro da
         organização, poderá acessar os serviços opcionais de todos os seus
         eventos
    """
    queryset = models.Service.objects.all().order_by('name')
    serializer_class = serializers.ServiceSerializer

    def get_serializer(self, *args, **kwargs):
        sub_pk = self.request.query_params.get('subscription', None)
        if sub_pk:
            kwargs.update({'subscription': sub_pk})
        return super().get_serializer(*args, **kwargs)

    # def get_queryset(self):
    #     user = self.request.user
    #
    #     # org_pks = [
    #     #     m.organization.pk
    #     #     for m in user.person.members.filter(active=True)
    #     # ]
    #
    #     queryset = super().get_queryset()
    #     return queryset.filter(
    #         lot_category__event__organization_id__in=org_pks
    #     )

    def filter_queryset(self, queryset: QuerySet) -> QuerySet:
        queryset = super().filter_queryset(queryset)

        show_inactive = self.request.query_params.get('show_inactive', None)

        if self.request.method == 'GET':
            if show_inactive is None \
                    or (show_inactive != '1' and show_inactive != 'true'):
                queryset = queryset.filter(published=True)

        return queryset

    def list(self, request, *args, **kwargs):
        event_pk = request.query_params.get('event', None)
        sub_pk = request.query_params.get('subscription', None)

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

        if sub_pk:
            try:
                uuid.UUID(sub_pk)
            except ValueError:
                content = {
                    'errors': [
                        "Subscription provided is a valid uuid",
                    ]
                }
                return Response(content, status=status.HTTP_400_BAD_REQUEST)

            try:
                Subscription.objects.exclude(
                    status=Subscription.CANCELED_STATUS
                ).get(
                    pk=sub_pk,
                    event_id=event_pk,
                    test_subscription=False,
                )
            except Subscription.DoesNotExist:
                content = {
                    'errors': [
                        "Subscription provided was not found",
                    ]
                }
                return Response(content, status=status.HTTP_404_NOT_FOUND)

        queryset = self.get_queryset()
        queryset = queryset.filter(lot_category__event_id=event_pk)

        page = self.paginate_queryset(self.filter_queryset(queryset))
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ProductViewSet(AuthenticatedViewSetMixin,
                     viewsets.ModelViewSet):
    """
         Essa view é responsavel por retornar o usuário, se membro da
         organização, poderá acessar os produtos opcionais de todos os seus
         eventos
    """
    queryset = models.Product.objects.all().order_by('name')
    serializer_class = serializers.ProductSerializer

    def get_serializer(self, *args: Any, **kwargs):
        sub_pk = self.request.query_params.get('subscription', None)
        if sub_pk:
            kwargs.update({'subscription': sub_pk})
        return super().get_serializer(*args, **kwargs)

    # def get_queryset(self):
    #     user = self.request.user
    #
    #     org_pks = [
    #         m.organization.pk
    #         for m in user.person.members.filter(active=True)
    #     ]
    #
    #     queryset = super().get_queryset()
    #     return queryset.filter(
    #         lot_category__event__organization_id__in=org_pks
    #     )

    def filter_queryset(self, queryset: QuerySet) -> QuerySet:
        queryset = super().filter_queryset(queryset)

        show_inactive = self.request.query_params.get('show_inactive', None)

        if show_inactive is None \
                or (show_inactive != '1' and show_inactive != 'true'):
            queryset = queryset.filter(published=True)

        return queryset

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


class SubscriptionServiceViewSet(AuthenticatedViewSetMixin,
                                 viewsets.ModelViewSet):
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


class SubscriptionProductViewSet(AuthenticatedViewSetMixin,
                                 viewsets.ModelViewSet):
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
