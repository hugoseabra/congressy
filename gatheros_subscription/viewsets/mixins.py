from rest_framework import permissions
from rest_framework.authentication import (
    SessionAuthentication,
    BasicAuthentication,
)

from project.token_authentication import ExpiringTokenAuthentication


class RestrictionViewMixin:
    authentication_classes = (
        SessionAuthentication,
        BasicAuthentication,
        ExpiringTokenAuthentication,
    )
    permission_classes = (
        permissions.IsAuthenticated,
    )
