from rest_framework import permissions
from rest_framework.authentication import (
    BasicAuthentication,
    SessionAuthentication,
)

from project.token_authentication import ExpiringTokenAuthentication


class RestrictionViewMixin(object):
    authentication_classes = (
        SessionAuthentication,
        BasicAuthentication,
        ExpiringTokenAuthentication,
    )
    permission_classes = (permissions.IsAuthenticated,)
