from typing import Any

from django.core.exceptions import PermissionDenied
from rest_framework import viewsets, status
from rest_framework.authentication import SessionAuthentication, \
    BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from gatheros_event.models import Event
from project.token_authentication import ExpiringTokenAuthentication
from sync.endpoint_permissions import (
    SyncClientOrganizerOnly,
    SyncQueueAllowedClientKey,
)
from sync.models import SyncClient, SyncQueue
from sync.serializers import SyncClientSerializer, SyncQueueSerializer


class SyncClientRestrictionMixin:
    authentication_classes = (
        SessionAuthentication,
        BasicAuthentication,
        ExpiringTokenAuthentication,
    )


class SyncClientViewSet(SyncClientRestrictionMixin, viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, SyncClientOrganizerOnly)
    serializer_class = SyncClientSerializer
    queryset = SyncClient.objects.get_queryset()

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        event = serializer.validated_data.get('event')

        members_qs = event.organization.members

        user_ids = [m.person.user_id for m in
                    members_qs.filter(active=True)
                    if m.person.user_id]

        if request.user.pk not in user_ids:
            raise PermissionDenied()

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:

        if not hasattr(request.user, 'person'):
            content = {
                'errors': ['user has not person', ]
            }

            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        person = request.user.person

        event_id = request.query_params.get('event_id', None)

        if event_id is None:
            content = {
                'errors': ['missing event_id in query', ]
            }

            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        try:
            event_id = int(event_id)

        except ValueError:
            content = {
                'errors': ["event_id in query is not int: '{}' ".format(
                    event_id), ]
            }

            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        try:
            event = Event.objects.get(pk=event_id)

        except Event.DoesNotExist:
            content = {
                'errors': ["event_id not valid: '{}' ".format(event_id), ]
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        if event.organization.is_member(person) is False:
            content = {
                'errors': ["event_id not allowed: '{}' ".format(event_id), ]
            }
            return Response(content, status=status.HTTP_403_FORBIDDEN)

        qs = SyncClient.objects.filter(event_id=event_id)

        queryset = self.filter_queryset(qs)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class SyncQueueViewSet(SyncClientRestrictionMixin, viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, SyncQueueAllowedClientKey)
    serializer_class = SyncQueueSerializer
    queryset = SyncQueue.objects.get_queryset()

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:

        if not hasattr(request.user, 'person'):
            content = {
                'errors': ['user has not person', ]
            }

            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        person = request.user.person

        event_id = request.query_params.get('event_id', None)

        if event_id is None:
            content = {
                'errors': ['missing event_id in query', ]
            }

            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        try:
            event_id = int(event_id)

        except ValueError:
            content = {
                'errors': ["event_id in query is not int: '{}' ".format(
                    event_id), ]
            }

            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        try:
            event = Event.objects.get(pk=event_id)

        except Event.DoesNotExist:
            content = {
                'errors': ["event_id not valid: '{}' ".format(event_id), ]
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        if event.organization.is_member(person) is False:
            content = {
                'errors': ["event_id not allowed: '{}' ".format(event_id), ]
            }
            return Response(content, status=status.HTTP_403_FORBIDDEN)

        qs = SyncQueue.objects.filter(client__event_id=event_id)

        queryset = self.filter_queryset(qs)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
