from typing import Any

from django.views import View
from rest_framework.permissions import BasePermission
from rest_framework.request import Request


class TicketOrganizerOnly(BasePermission):
    """
    Allows access only to organizers
    """

    def has_object_permission(self, request: Request, view: View,
                              obj: Any) -> bool:
        """
         via the object being fetched
        :param request:
        :param view:
        :param obj:
        :return:
        """

        event_organizers = [m.person.user for m in
                            obj.event.organization.members.filter(active=True)]

        return request.user in event_organizers


class LotOrganizerOnly(BasePermission):
    """
    Allows access only to organizers
    """

    def has_object_permission(self, request: Request, view: View,
                              obj: Any) -> bool:
        """
         via the object being fetched
        :param request:
        :param view:
        :param obj:
        :return:
        """

        event_organizers = [m.person.user for m in
                            obj.ticket.event.organization.members.filter(
                                active=True)]

        return request.user in event_organizers
