from typing import Any

from django.views import View
from rest_framework.permissions import BasePermission
from rest_framework.request import Request

from gatheros_event.models import Event


class OrganizerOnlyByKwargs(BasePermission):
    """
    Allows access only to organizers via a event_pk passed in parameter of
    the url.
    """

    def has_permission(self, request, view):
        qs = Event.objects.filter(
            organization__members__person__user=request.user
        )

        event_pks = [str(event.pk) for event in qs]

        return view.kwargs['event_pk'] in event_pks


class OrganizerOnlyByObj(BasePermission):
    """
    Allows access only to organizers via the object being fetched
    """

    def has_object_permission(self, request: Request, view: View,
                              obj: Any) -> bool:
        raise Exception("Not implemented")
