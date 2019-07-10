from typing import Any

from django.views import View
from rest_framework.permissions import BasePermission
from rest_framework.request import Request


class SyncClientOrganizerOnly(BasePermission):
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

        members_qs = obj.event.organization.members

        user_ids = [
            m.person.user_id
            for m in members_qs.filter(active=True)
            if m.person.user_id
        ]

        return request.user.pk in user_ids


class SyncQueueAllowedClientKey(BasePermission):
    """
    Allows access only to correct sync client key
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
        key = request.query_params.get('sync_client_key')

        if not key:
            return False

        client = obj.client

        if client.active is False:
            return False

        if client.key != key:
            return False

        members_qs = obj.client.event.organization.members

        user_ids = [
            m.person.user_id
            for m in members_qs.filter(active=True)
            if m.person.user_id
        ]

        return request.user.pk in user_ids
