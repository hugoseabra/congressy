from rest_framework import permissions


class RestrictionViewMixin(object):
    permission_classes = (permissions.IsAuthenticated,)
