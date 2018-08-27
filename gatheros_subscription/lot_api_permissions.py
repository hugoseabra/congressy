from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.permissions import BasePermission

from gatheros_event.models import Event


class MultiLotsAllowed(BasePermission):
    """
        Allows access only events with flag enabled
    """

    def has_permission(self, request, view):
        event_pk = view.kwargs.get('event_pk')
        try:

            event = Event.objects.get(pk=event_pk)

            if not event.feature_configuration.feature_multi_lots:
                raise PermissionDenied()

        except ObjectDoesNotExist:
            raise NotFound()

        return True
