from rest_framework import permissions


class RestrictionViewMixin:
    permission_classes = (
        permissions.IsAuthenticated,
    )
