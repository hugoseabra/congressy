from django.db.models import Q
from rest_framework import viewsets, generics, pagination
from rest_framework.authentication import (
    BasicAuthentication,
    SessionAuthentication,
)
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.util.string import clear_string
from gatheros_subscription.lot_api_permissions import MultiLotsAllowed
from gatheros_subscription.models import Subscription
from gatheros_subscription.serializers import (
    Lot,
    LotSerializer,
    SubscriptionSerializer,
)
from .permissions import OrganizerOnly


class RestrictionViewMixin:
    authentication_classes = (SessionAuthentication, BasicAuthentication)


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

    def list(self, request, *args, **kwargs):
        queryset = self.filter(request, self.get_queryset())
        queryset = self.get_order_by(request, queryset)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

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

    def filter(self, request, queryset):

        search_param = request.query_params.get("search")

        if search_param is None or search_param == '':
            return queryset

        return queryset.filter(
            Q(uuid=search_param, ) |
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
