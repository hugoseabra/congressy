from rest_framework import permissions
from rest_framework.authentication import (
    BasicAuthentication,
    SessionAuthentication,
    TokenAuthentication,
)
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet

from gatheros_event.models import Organization, Event, Person
from gatheros_event.serializers import (
    EventSerializer,
    OrganizationSerializer,
    PersonSerializer,
)


class PersonViewSet(ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    permission_classes = (
        permissions.IsAuthenticated,
    )
    authentication_classes = (
        BasicAuthentication,
        SessionAuthentication,
        TokenAuthentication,
    )

    def list(self, request, *args, **kwargs):
        content = {
            'detail': 'request is not allowed.'
        }
        return Response(content, status=405)

    def check_permissions(self, request):
        super().check_permissions(request)

        user = self.request.user
        person = user.person if hasattr(user, 'person') else None
        person_pk = self.kwargs.get('pk')

        if not person or str(person.pk) != person_pk:
            self.permission_denied(
                request,
                message='Permissão negada'
            )


class OrganizationReadOnlyViewSet(ReadOnlyModelViewSet):
    serializer_class = OrganizationSerializer
    queryset = Organization.objects.all()
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
    )
    authentication_classes = (
        BasicAuthentication,
        SessionAuthentication,
        TokenAuthentication,
    )

    def permission_denied(self, request, message=None):
        """
        If request is not permitted, determine what kind of exception to raise.
        ALWAYS RAISE A PERMISSION DENIED - WTF DJANGO REST ????
        """
        raise PermissionDenied(detail=message)

    def list(self, request, *args, **kwargs):

        org_pks = list()

        if hasattr(request.user, 'person'):

            for m in request.user.person.members.filter(active=True):
                org_pks.append(m.organization_id)

        queryset = Organization.objects.filter(
            pk__in=org_pks
        ).order_by("name")

        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class EventReadOnlyViewSet(ReadOnlyModelViewSet):
    serializer_class = EventSerializer
    queryset = Event.objects.all()
    lookup_field = 'slug'
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
    )
    authentication_classes = (
        BasicAuthentication,
        SessionAuthentication,
        TokenAuthentication,
    )

    def permission_denied(self, request, message=None):
        """
        If request is not permitted, determine what kind of exception to raise.
        ALWAYS RAISE A PERMISSION DENIED - WTF DJANGO REST ????
        """
        raise PermissionDenied(detail=message)

    def list(self, request, *args, **kwargs):

        org_pks = list()

        if hasattr(request.user, 'person'):
            for m in request.user.person.members.filter(active=True):
                org_pks.append(m.organization_id)

        queryset = Event.objects.filter(
            organization_id__in=org_pks
        ).order_by("name")

        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
