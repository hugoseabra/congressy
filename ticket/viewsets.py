from typing import Any

from django.core.exceptions import PermissionDenied
from rest_framework import viewsets, status
from rest_framework.authentication import SessionAuthentication, \
    BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from gatheros_subscription.models import Subscription
from ticket.models import Ticket, Lot
from ticket.serializers import TicketSerializer, LotSerializer
from .permissions import OrganizerOnly


class TicketRestrictionMixin:
    permission_classes = (IsAuthenticated, OrganizerOnly)
    authentication_classes = (
        SessionAuthentication,
        BasicAuthentication,
        TokenAuthentication,
    )


class TicketViewSet(TicketRestrictionMixin, viewsets.ModelViewSet):
    serializer_class = TicketSerializer
    queryset = Ticket.objects.all()

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        event = serializer.validated_data.get('event')

        event_organizers = [m.person.user for m in
                            event.organization.members.filter(active=True)]

        if request.user not in event_organizers:
            raise PermissionDenied()

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:

        events = list()

        if hasattr(request.user, 'person'):

            for m in request.user.person.members.filter(active=True):

                organization = m.organization

                for event in organization.events.all():
                    if event not in events:
                        events.append(event.pk)

        qs = Ticket.objects.filter(
            event_id__in=events,
        )

        queryset = self.filter_queryset(qs)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:

        instance = self.get_object()

        if self._ticket_has_subscriptions(instance):
            return Response(status=status.HTTP_409_CONFLICT)

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def _ticket_has_subscriptions(ticket: Ticket):

        return bool(
            Subscription.objects.filter(
                ticket_lot__ticket_id=ticket.pk,
                test_subscription=False,
                completed=True,
                status=Subscription.CONFIRMED_STATUS,
            ).count()
        )


class LotViewSet(TicketRestrictionMixin, viewsets.ModelViewSet):
    serializer_class = LotSerializer
    queryset = Lot.objects.all()
