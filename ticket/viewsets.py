from typing import Any

from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.authentication import SessionAuthentication, \
    BasicAuthentication, TokenAuthentication
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from gatheros_event.models import Event
from gatheros_subscription.models import Subscription
from ticket.helpers import (
    get_lot_price_for_audience,
    get_lot_price_for_organizer,
    get_lot_installment_prices_for_audience,
    get_lot_installment_prices_for_organizer,
    get_max_installments_allowed_for_price,
)
from ticket.models import Ticket, Lot
from ticket.serializers import TicketSerializer, LotSerializer
from .permissions import TicketOrganizerOnly, LotOrganizerOnly


class CurrentLotNotFoundError(Exception):
    pass


class TicketRestrictionMixin:
    authentication_classes = (
        SessionAuthentication,
        BasicAuthentication,
        TokenAuthentication,
    )


class TicketViewSet(TicketRestrictionMixin, viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, TicketOrganizerOnly)
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

        event_id = request.query_params.get('event_id', None)

        if event_id is None:
            content = {
                'errors': ['missing event_id in query', ]
            }

            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        else:

            try:
                event_id = int(event_id)
            except ValueError:
                content = {
                    'errors': ["event_id in query is not int: '{}' ".format(event_id), ]
                }

                return Response(content, status=status.HTTP_400_BAD_REQUEST)

            events = list()

            if hasattr(request.user, 'person'):

                for m in request.user.person.members.filter(active=True):

                    organization = m.organization

                    for event in organization.events.all():
                        if event not in events:
                            events.append(event.pk)

            qs = Ticket.objects.filter(
                event_id__in=events,
                event_id=event_id,
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


class TicketCalculatorAPIView(TicketRestrictionMixin, APIView):
    permission_classes = (IsAuthenticated,)

    # noinspection PyMethodMayBeStatic
    def get(self, request, *_, **kwargs):
        event = get_object_or_404(Event, pk=kwargs['event_pk'])

        transfer_tax = request.query_params.get("transfer_tax", False)
        free_installments = request.query_params.get("free_installments", 0)

        members = [
            m.person
            for m in event.organization.members.filter(active=True)
        ]

        if request.user.person not in members:
            content = {
                'detail': 'unauthorized'
            }

            return Response(content, status=status.HTTP_401_UNAUTHORIZED)

        price_allowed_installments = \
            get_max_installments_allowed_for_price(kwargs['price'])

        installment_lists = {
            'audience_installments':
                get_lot_installment_prices_for_audience(
                    price=kwargs['price'],
                    cgsy_percent=event.congressy_percent,
                    transfer_tax=transfer_tax,
                    free_installments=free_installments,
                    installments=price_allowed_installments,
                ),

            'organizer_installments':
                get_lot_installment_prices_for_organizer(
                    price=kwargs['price'],
                    cgsy_percent=event.congressy_percent,
                    transfer_tax=transfer_tax,
                    free_installments=free_installments,
                    installments=price_allowed_installments,
                ),
        }

        data = {

            'event': event.pk,
            'transfer_tax': transfer_tax,
            'free_installments': free_installments,
            'congressy_percent': event.congressy_percent,

            'price': get_lot_price_for_audience(
                raw_price=kwargs['price'],
                cgsy_percent=event.congressy_percent,
                transfer_tax=event.transfer_tax
            ),

            'liquid_price': get_lot_price_for_organizer(
                raw_price=kwargs['price'],
                cgsy_percent=event.congressy_percent,
                transfer_tax=event.transfer_tax
            ),

            'allowed_installments': price_allowed_installments,

            'installments': installment_lists,

        }

        return Response(data, status=status.HTTP_200_OK)


class TicketCurrentLotView(TicketRestrictionMixin, RetrieveAPIView):
    serializer_class = LotSerializer

    def retrieve(self, request, *args, **kwargs):

        try:
            instance = self.get_object()
        except Ticket.DoesNotExist:
            return Response({"detail": "Ticket not found."},
                            status=status.HTTP_404_NOT_FOUND)
        except CurrentLotNotFoundError:
            return Response({"detail": "Lot not found."},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_object(self):
        """
        Returns the object the view is displaying.
        """

        user = self.request.user
        ticket_pk = self.kwargs.get('pk')

        org_pks = [
            m.organization.pk
            for m in user.person.members.filter(active=True)
        ]

        ticket = Ticket.objects.get(
            pk=ticket_pk,
            event__organization_id__in=org_pks,
        )

        obj = ticket.current_lot
        if obj is None:
            raise CurrentLotNotFoundError()

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj


class LotViewSet(TicketRestrictionMixin, viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, LotOrganizerOnly)
    serializer_class = LotSerializer
    queryset = Lot.objects.all()

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ticket = serializer.validated_data.get('ticket')

        event = ticket.event

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

        ticket_id = request.query_params.get('ticket_id', None)

        if ticket_id is None:
            content = {
                'errors': ['missing ticket_id in query', ]
            }

            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        else:

            try:
                ticket_id = int(ticket_id)
            except ValueError:
                content = {
                    'errors': ["ticket_id in query is not int: '{}' ".format(ticket_id), ]
                }

                return Response(content, status=status.HTTP_400_BAD_REQUEST)

            events = list()

            if hasattr(request.user, 'person'):

                for m in request.user.person.members.filter(active=True):

                    organization = m.organization

                    for event in organization.events.all():
                        if event not in events:
                            events.append(event.pk)

            qs = Lot.objects.filter(
                ticket__event_id__in=events,
                ticket_id=ticket_id
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
    def _ticket_has_subscriptions(lot: Lot):

        return bool(
            Subscription.objects.filter(
                ticket_lot_id=lot.pk,
                test_subscription=False,
                completed=True,
                status=Subscription.CONFIRMED_STATUS,
            ).count()
        )
