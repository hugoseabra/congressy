from rest_framework import permissions, status
from rest_framework.authentication import (
    BasicAuthentication,
    SessionAuthentication,
)
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import (
    GenericViewSet,
    ModelViewSet,
    ReadOnlyModelViewSet,
)

from core.viewsets import (
    AuthenticatedViewSetMixin,
    AuthenticatedOrReadOnlyViewSetMixin,
)
from gatheros_event.models import Organization, Event, Person
from gatheros_event.serializers import (
    EventSerializer,
    OrganizationSerializer,
    PersonSerializer,
)
from project.token_authentication import ExpiringTokenAuthentication


class PersonViewSet(AuthenticatedViewSetMixin, ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer

    def list(self, request, *args, **kwargs):
        content = {
            'detail': 'request is not allowed.'
        }
        return Response(content, status=405)

    def create(self, request, *args, **kwargs):
        """ Só se cria person vinculado ao usuário. """
        user_pk = request.data.get('user')

        serializer = self.get_serializer(data=request.data)
        is_new = True

        if user_pk:
            persons = Person.objects.filter(user_id=user_pk)
            if persons.count():
                instance = persons.order_by('created').first()

                self.check_object_permissions(self.request, instance)

                serializer = self.get_serializer(instance=instance,
                                                 data=request.data,
                                                 partial=True, )
                is_new = False

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

    def check_permissions(self, request):
        super().check_permissions(request)

        if request.method != 'POST':
            user = self.request.user
            person = user.person if hasattr(user, 'person') else None
            person_pk = self.kwargs.get('pk')

            if not person or str(person.pk) != person_pk:
                self.permission_denied(
                    request,
                    message='Permissão negada'
                )


class PersonLoggedUserViewSet(AuthenticatedViewSetMixin,
                              GenericViewSet,
                              ListModelMixin):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        return queryset.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        obj = queryset.order_by('created').first()

        serializer = self.get_serializer(obj)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return Response(serializer.data)


class OrganizationReadOnlyViewSet(AuthenticatedOrReadOnlyViewSetMixin,
                                  ReadOnlyModelViewSet):
    serializer_class = OrganizationSerializer
    queryset = Organization.objects.all()

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

        queryset = Organization.objects.filter(pk__in=org_pks).order_by("name")

        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class EventReadOnlyViewSet(AuthenticatedOrReadOnlyViewSetMixin,
                           ReadOnlyModelViewSet):
    serializer_class = EventSerializer
    queryset = Event.objects.all()

    def get_object(self):
        pk = self.kwargs.get('pk')  # default

        if str(pk).isdigit():
            return super().get_object()

        queryset = self.get_queryset()  # Get the base queryset
        queryset = self.filter_queryset(queryset)  # Apply any filter backends

        obj = get_object_or_404(queryset, published=True, slug=pk)  # Lookup the object
        self.check_object_permissions(self.request, obj)
        return obj

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
