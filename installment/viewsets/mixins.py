from rest_framework import permissions
from rest_framework.authentication import (
    BasicAuthentication,
    SessionAuthentication,
)


class RestrictionViewMixin(object):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
