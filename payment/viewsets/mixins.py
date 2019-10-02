from rest_framework import permissions
from rest_framework.authentication import (
    BasicAuthentication,
    SessionAuthentication,
    TokenAuthentication,
)


class RestrictionViewMixin(object):
    authentication_classes = (
        SessionAuthentication,
        BasicAuthentication,
        TokenAuthentication,
    )
    permission_classes = (permissions.IsAuthenticated,)
