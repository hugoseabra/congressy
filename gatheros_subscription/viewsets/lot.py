from datetime import datetime

from rest_framework import viewsets, status, permissions
from rest_framework.response import Response

from core.viewsets import AuthenticatedViewSetMixin
from gatheros_subscription.models import Lot
from gatheros_subscription.serializers import (
    LotSerializer,
)


class LotViewSet(AuthenticatedViewSetMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Lot.objects.all().order_by('name')
    serializer_class = LotSerializer

    def get_queryset(self):
        # user = self.request.user

        queryset = super().get_queryset()

        # if hasattr(user, 'person'):
        #     org_pks = [
        #         m.organization.pk
        #         for m in user.person.members.filter(active=True)
        #     ]
        #
        #     queryset = queryset.filter(event__organization__in=org_pks)

        return queryset.order_by('name')

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

        exhibition_code = \
            self.request.query_params.get('exhibition_code', None)
        show_private = self.request.query_params.get('show_private', None)
        show_inactive = self.request.query_params.get('show_inactive', None)
        ignore_dates = self.request.query_params.get('ignore_dates', None)

        if exhibition_code:
            queryset = queryset.filter(
                exhibition_code=exhibition_code.upper(),
            )

        elif show_private is None \
                or (show_private != '1' and show_private != 'true'):
            queryset = queryset.filter(private=False)

        if show_inactive is None \
                or (show_inactive != '1' and show_inactive != 'true'):
            queryset = queryset.filter(active=True)

        if ignore_dates is None \
                or (ignore_dates != '1' and ignore_dates != 'true'):
            now = datetime.now()
            queryset = queryset.filter(
                date_start__lte=now,
                date_end__gte=now,
            )

        return queryset

    def check_permissions(self, request):
        """
        Check if the request should be permitted.
        Raises an appropriate exception if the request is not permitted.

        Special case: Viewset does not allow object creation without
        the multi-lot flag enabled.
        """

        if request.method not in ("POST", "PATCH"):
            self.permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

        for permission in self.get_permissions():
            if not permission.has_permission(request, self):
                self.permission_denied(
                    request, message=getattr(permission, 'message', None)
                )
