from datetime import datetime
from time import sleep
from typing import Any

from django.db.models import Q
from django.http import HttpResponse
from rest_framework import viewsets, generics, pagination, status, permissions
from rest_framework.authentication import (
    BasicAuthentication,
    SessionAuthentication,
)
from rest_framework.exceptions import APIException
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from core.util.string import clear_string
from gatheros_event.models import Event
from gatheros_subscription.helpers.subscription_async_exporter import \
    SubscriptionServiceAsyncExporter
from gatheros_subscription.models import Subscription, Lot
from gatheros_subscription.permissions import OrganizerOnly
from gatheros_subscription.serializers import (
    SubscriptionSerializer,
    SubscriptionModelSerializer,
    SubscriptionBillingSerializer, SubscriptionPaymentSerializer)
from gatheros_subscription.tasks import async_subscription_exporter_task
from project.token_authentication import ExpiringTokenAuthentication
from .mixins import RestrictionViewMixin


class DatatablePagination(pagination.LimitOffsetPagination):
    page_size = 10

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'recordsTotal': self.count,
            'recordsFiltered': self.count,
            'data': data
        })


class SubscriptionListViewSet(RestrictionViewMixin,
                              generics.GenericAPIView):
    """
    API endpoint for the subscription list view
    """
    serializer_class = SubscriptionSerializer
    pagination_class = DatatablePagination

    permission_classes = (IsAuthenticated, OrganizerOnly)

    def get_queryset(self):
        event_pk = self.kwargs['event_pk']

        return Subscription.objects.filter(
            event_id=event_pk,
            completed=True,
        )

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def list(self, request, *_, **__):
        queryset = self.filter(request, self.get_queryset())
        queryset = self.get_order_by(request, queryset)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # noinspection PyMethodMayBeStatic
    def get_order_by(self, request, queryset):

        required = [
            'filter_by',
            'dir',
        ]

        has_required = True

        for param in required:
            if param not in request.query_params:
                has_required = False

        if has_required is False:
            return queryset

        column = request.query_params.get('filter_by')
        direction = request.query_params.get('dir')

        if column == "0":
            field = 'person__name'
        elif column == "2":
            field = 'lot__name'
        elif column == "3":
            field = 'event_count'
        else:
            raise APIException("Unknown column: {}".format(column))

        order = ""
        if direction == "desc":
            order = "-"

        return queryset.order_by(order + field)

    # noinspection PyMethodMayBeStatic
    def filter(self, request, queryset):

        search_param = request.query_params.get("search")
        tag_group_param = request.query_params.get("tag_group")
        category_param = request.query_params.get("category")
        lot_param = request.query_params.get("lot")

        if tag_group_param and tag_group_param != '':
            queryset = queryset.filter(
                tag_group=tag_group_param,
            )

        if category_param and category_param != '':
            queryset = queryset.filter(
                lot__category__id=category_param,
            )

        if lot_param and lot_param != '':
            queryset = queryset.filter(
                lot__id=lot_param,
            )

        if search_param is None or search_param == '':
            return queryset

        return queryset.filter(
            Q(code=search_param, ) |
            Q(lot__name__icontains=search_param, ) |
            Q(lot__category__name__icontains=search_param, ) |
            Q(person__name__icontains=search_param, ) |
            Q(person__email__icontains=search_param, ) |
            Q(person__cpf__icontains=clear_string(search_param), ) |
            Q(person__phone__icontains=search_param, ) |
            Q(person__international_doc__icontains=search_param, ) |
            Q(person__city__name__icontains=search_param, ) |
            Q(person__city__name_ascii__icontains=search_param, ) |
            Q(person__city__uf__icontains=search_param, ) |
            Q(person__city_international__icontains=search_param, ) |
            Q(person__cpf__icontains=search_param, ) |
            Q(person__institution_cnpj__icontains=search_param, )
        )


class SubscriptionExporterViewSet(RestrictionViewMixin, APIView):
    permission_classes = (OrganizerOnly,)

    def post(self, request, *args, **kwargs):
        event_pk = kwargs.get('event_pk')

        if not event_pk:
            return Response({'error: missing event_pk'},
                            status=status.HTTP_400_BAD_REQUEST)

        event = Event.objects.get(pk=event_pk)

        exporter = SubscriptionServiceAsyncExporter(event)

        if exporter.has_export_lock():
            return Response(status=status.HTTP_204_NO_CONTENT)

        exporter.create_export_lock()

        lock = True
        lock_count = 0

        while lock:
            sleep(2)

            exporter = SubscriptionServiceAsyncExporter(event)

            if exporter.has_export_lock():
                async_subscription_exporter_task.delay(event_pk=event.pk)
                return Response(status=status.HTTP_201_CREATED)

            lock_count += 1

            if lock_count >= 10:
                lock = False

        return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request, *args, **kwargs):

        event_pk = kwargs.get('event_pk')

        if not event_pk:
            return Response({'error: missing event_pk'},
                            status=status.HTTP_400_BAD_REQUEST)

        event = Event.objects.get(pk=event_pk)

        exporter = SubscriptionServiceAsyncExporter(event)

        if exporter.has_export_lock():
            return Response(status=status.HTTP_204_NO_CONTENT)

        if not exporter.has_existing_export_files():
            return Response(status=status.HTTP_404_NOT_FOUND)

        # Criando resposta http com arquivo de download
        # Reading file
        file_name = exporter.get_export_file_path()

        output = open(file_name, mode='rb').read()
        name = "%s_%s.xlsx" % (
            event.slug,
            datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        )

        response = HttpResponse(
            output,
            content_type="application/vnd.ms-excel"
        )

        response['Content-Disposition'] = 'attachment; filename=%s' % name

        return response


class SubscriptionViewSet(RestrictionViewMixin, viewsets.ModelViewSet):
    serializer_class = SubscriptionModelSerializer
    queryset = Subscription.objects.all()
    permission_classes = (
        permissions.IsAuthenticated,
    )

    # def get_queryset(self):
    #     user = self.request.user
    #
    #     org_pks = list()
    #
    #     if hasattr(user, 'person'):
    #
    #         for m in user.person.members.filter(active=True):
    #             org_pks.append(m.organization_id)
    #
    #     queryset = super().get_queryset()
    #     return queryset.filter(event__organization_id__in=org_pks)

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:

        event_id = request.query_params.get('event', None)

        if event_id is None:
            content = {
                'errors': ['missing event in query string', ]
            }

            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        try:
            event_id = int(event_id)
        except ValueError:
            content = {
                'errors': ["event in query is not int: '{}' ".format(
                    event_id), ]
            }

            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        qs = self.get_queryset()
        qs = qs.filter(event_id=event_id)

        incompleted = request.query_params.get('incompleted')
        test_subscription = request.query_params.get('test_subscription')

        if incompleted is None:
            qs = qs.filter(completed=True)
        else:
            qs = qs.filter(completed=False)

        if test_subscription is None:
            qs = qs.filter(test_subscription=False)

        queryset = self.filter_queryset(qs)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """ Só se cria person vinculado ao usuário. """
        person_pk = request.data.get('person')
        lot_pk = request.data.get('lot')

        serializer = self.get_serializer(data=request.data)
        is_new = True

        if person_pk:
            try:
                lot = Lot.objects.get(pk=lot_pk)
            except Lot.DoesNotExist:
                content = {
                    'errors': ["Lote não encontrado: '{}' ".format(lot_pk)]
                }
                return Response(content, status=status.HTTP_400_BAD_REQUEST)

            try:
                instance = Subscription.objects.get(
                    person_id=person_pk,
                    lot__event_id=lot.event_id,
                )
                self.check_object_permissions(self.request, instance)

                if instance.lot_id != int(lot_pk):
                    content = {
                        'detail': [
                            'Esta pessoa já está inscrita neste evento e'
                            ' você está tentando alterar o lote por este'
                            ' método. Isso não é possível.'
                        ]
                    }
                    return Response(content, status=status.HTTP_403_FORBIDDEN)

                serializer = self.get_serializer(instance=instance,
                                                 data=request.data,
                                                 partial=True, )
                is_new = False

            except Subscription.DoesNotExist:
                pass

        serializer.is_valid(raise_exception=True)

        if is_new:
            self.perform_create(serializer)
            resp_status = status.HTTP_201_CREATED
        else:
            self.perform_update(serializer)
            resp_status = status.HTTP_200_OK

            if getattr(serializer.instance, '_prefetched_objects_cache', None):
                # If 'prefetch_related' has been applied to a queryset,
                # we need forcibly invalidate the prefetch cache on the
                # instance.
                serializer.instance._prefetched_objects_cache = {}

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,
                        status=resp_status,
                        headers=headers)

    def update(self, request, *args, **kwargs):

        person_pk = request.data.get('person')
        lot_pk = request.data.get('lot')

        serializer = self.get_serializer(data=request.data)
        is_new = True

        if person_pk:
            try:
                lot = Lot.objects.get(pk=lot_pk)
            except Lot.DoesNotExist:
                content = {
                    'errors': ["Lote não encontrado: '{}' ".format(lot_pk)]
                }
                return Response(content, status=status.HTTP_400_BAD_REQUEST)

            try:
                instance = Subscription.objects.get(
                    person_id=person_pk,
                    lot__event_id=lot.event_id,
                )
                self.check_object_permissions(self.request, instance)

                if instance.lot_id != int(lot_pk):
                    content = {
                        'detail': [
                            'Esta pessoa já está inscrita neste evento e'
                            ' você está tentando alterar o lote por este'
                            ' método. Isso não é possível.'
                        ]
                    }
                    return Response(content, status=status.HTTP_403_FORBIDDEN)

                serializer = self.get_serializer(instance=instance,
                                                 data=request.data,
                                                 partial=True, )
                is_new = False

            except Subscription.DoesNotExist:
                pass

        return super().update(request, *args, **kwargs)


class SubscriptionBillingViewSet(GenericViewSet, RetrieveModelMixin):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionBillingSerializer
    permission_classes = (
        permissions.IsAuthenticated,
    )
    authentication_classes = (
        BasicAuthentication,
        SessionAuthentication,
        ExpiringTokenAuthentication,
    )


class SubscriptionPaymentViewSet(GenericViewSet, RetrieveModelMixin):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionPaymentSerializer
    permission_classes = (
        permissions.IsAuthenticated,
    )
    authentication_classes = (
        BasicAuthentication,
        SessionAuthentication,
        ExpiringTokenAuthentication,
    )


class SubscriptionEventViewSet(GenericViewSet, RetrieveModelMixin):
    queryset = Subscription.objects.get_queryset()
    serializer_class = SubscriptionSerializer
    permission_classes = (
        permissions.IsAuthenticated,
    )
    authentication_classes = (
        BasicAuthentication,
        SessionAuthentication,
        ExpiringTokenAuthentication,
    )

    lookup_field = 'event_pk'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event = None
        self.person = None

    def get_person(self):
        if self.person:
            return self.person

        user = self.request.user

        if not hasattr(user, 'person'):
            return None

        self.person = user.person
        return self.person

    def get_event(self):
        if self.event:
            return self.event

        pk = self.kwargs.get('event_pk')  # default

        if str(pk).isdigit():
            try:
                self.event = Event.objects.get(pk=pk)
            except Event.DoesNotExist:
                pass

        if self.event is None:
            try:
                self.event = Event.objects.get(slug=str(pk))
            except Event.DoesNotExist:
                pass

        return self.event

    def retrieve(self, request, *args, **kwargs):
        event = self.get_event()
        person = self.get_person()

        if not event:
            content = {
                'errors': [
                    "Evento não encontrado: '{}' ".format(
                        self.kwargs.get('event_pk')
                    )
                ]
            }
            return Response(content, status=status.HTTP_404_NOT_FOUND)

        if not person:
            content = {
                'errors': ["Usuário não possui pessoa relacionada"]
            }
            return Response(content, status=status.HTTP_404_NOT_FOUND)

        instance = self.get_object()
        if not instance:
            content = {
                'errors': ["Usuário não possui inscrição neste evento"]
            }
            return Response(content, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_queryset(self):
        event = self.get_event()
        person = self.get_person()

        queryset = super().get_queryset()

        try:
            queryset = queryset.get(
                event_id=event.pk,
                person_id=person.pk,
            )
        except Subscription.DoesNotExist:
            return queryset.none()

        return queryset

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())

        # May raise a permission denied
        self.check_object_permissions(self.request, queryset)

        return queryset
