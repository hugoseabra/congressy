from rest_framework.permissions import BasePermission

from gatheros_event.models import Event


class OrganizerOnlyByKwargs(BasePermission):
    """
    Allows access only to authenticated users.
    """

    def has_permission(self, request, view):
        qs = Event.objects.filter(
            organization__members__person__user=request.user
        )

        event_pks = [str(event.pk) for event in qs]

        return view.kwargs['event_pk'] in event_pks
