from rest_framework import permissions
from rest_framework.authentication import BasicAuthentication, SessionAuthentication, TokenAuthentication
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from gatheros_event.models import Event
from gatheros_event.serializers import EventReadOnlySerializer


class ReadPublishedEventsOnly(permissions.BasePermission):
    message = 'Only organizers can access unpublished events.'

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):

        if not request.user or not request.user.is_authenticated():
            return obj.published

        if hasattr(request.user, 'person'):

            for m in request.user.person.members.filter(active=True):

                organization = m.organization

                for event in organization.events.all():
                    if event.pk == obj.pk:
                        return True

        return obj.published


class EventReadOnlyViewSet(ReadOnlyModelViewSet):
    serializer_class = EventReadOnlySerializer
    queryset = Event.objects.all()
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    permission_classes = (ReadPublishedEventsOnly,)

    def permission_denied(self, request, message=None):
        """
        If request is not permitted, determine what kind of exception to raise.
        ALWAYS RAISE A PERMISSION DENIED - WTF DJANGO REST ????
        """
        raise PermissionDenied(detail=message)

    def list(self, request, *args, **kwargs):

        events = list()

        if hasattr(request.user, 'person'):

            for m in request.user.person.members.filter(active=True):

                organization = m.organization

                for event in organization.events.all():
                    if event not in events:
                        events.append(event.pk)

        queryset = Event.objects.filter(pk__in=events).order_by("created")

        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
