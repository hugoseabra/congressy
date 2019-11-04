from rest_framework import permissions
from rest_framework.authentication import (
    SessionAuthentication,
    BasicAuthentication,
    TokenAuthentication,
)


class RestrictionViewMixin:
    authentication_classes = (
        SessionAuthentication,
        BasicAuthentication,
        TokenAuthentication,
    )
    permission_classes = (
        permissions.IsAuthenticated,
    )
