from rest_framework.authentication import (
    SessionAuthentication,
    BasicAuthentication,
)
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)

from project.token_authentication import ExpiringTokenAuthentication


class AuthenticatedViewSetMixin(object):
    authentication_classes = (ExpiringTokenAuthentication,
                              SessionAuthentication,
                              BasicAuthentication)
    permission_classes = (IsAuthenticated,)


class AuthenticatedOrReadOnlyViewSetMixin(object):
    authentication_classes = (ExpiringTokenAuthentication,
                              SessionAuthentication,
                              BasicAuthentication)
    permission_classes = (IsAuthenticatedOrReadOnly,)
