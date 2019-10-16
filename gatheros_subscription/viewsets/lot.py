from datetime import datetime
from time import sleep
from typing import Any

from django.db.models import Q
from django.http import HttpResponse
from rest_framework import viewsets, generics, pagination, status, permissions
from rest_framework.authentication import (
    BasicAuthentication,
    SessionAuthentication,
    TokenAuthentication,
)
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.util.string import clear_string
from gatheros_event.models import Event
from gatheros_subscription.helpers.subscription_async_exporter import \
    SubscriptionServiceAsyncExporter
from gatheros_subscription.lot_api_permissions import MultiLotsAllowed
from gatheros_subscription.models import Lot, Subscription
from gatheros_subscription.serializers import (
    LotSerializer,
    SubscriptionSerializer,
    SubscriptionModelSerializer,
)
from gatheros_subscription.tasks import async_subscription_exporter_task
from gatheros_subscription.permissions import OrganizerOnly


class RestrictionViewMixin:
    authentication_classes = (
        SessionAuthentication,
        BasicAuthentication,
        TokenAuthentication,
    )


class LotViewSet(RestrictionViewMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Lot.objects.all().order_by('name')
    serializer_class = LotSerializer

    def get_queryset(self):
        user = self.request.user

        org_pks = [
            m.organization.pk
            for m in user.person.members.filter(active=True)
        ]

        queryset = super().get_queryset()
        return queryset.filter(event__organization__in=org_pks)

    def list(self, request, *args, **kwargs):
        event_pk = request.query_params.get('event', None)

        if event_pk is None:
            content = {
                'errors': ['missing event in query', ]
            }

            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        try:
            event_pk = int(event_pk)
        except ValueError:
            content = {
                'errors': [
                    "event in query is not int: '{}' ".format(event_pk),
                ]
            }

            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        queryset = self.get_queryset()
        queryset = queryset.filter(event_id=event_pk)

        page = self.paginate_queryset(self.filter_queryset(queryset))
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)

        exhibition_code = self.request.query_params.get('exhibition_code',
                                                        None)

        show_inactive = self.request.query_params.get('show_inactive', None)

        if show_inactive is None \
                or (show_inactive != '1' and show_inactive != 'true'):
            queryset = queryset.filter(active=True)

        if exhibition_code:
            exhibition_qs = queryset.filter(
                exhibition_code=exhibition_code,
                private=True,
            )
            queryset = exhibition_qs | queryset.filter(private=False, )
        else:
            queryset = queryset.filter(private=False, )

        return queryset

    def check_permissions(self, request):
        """
        Check if the request should be permitted.
        Raises an appropriate exception if the request is not permitted.

        Special case: Viewset does not allow object creation without
        the multi-lot flag enabled.
        """

        if request.method == "POST":
            self.permission_classes = (IsAuthenticated, MultiLotsAllowed)
        else:
            self.permission_classes = (IsAuthenticated,)

        for permission in self.get_permissions():
            if not permission.has_permission(request, self):
                self.permission_denied(
                    request, message=getattr(permission, 'message', None)
                )
