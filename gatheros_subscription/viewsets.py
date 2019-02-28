from rest_framework import viewsets, generics
from rest_framework.authentication import (
    BasicAuthentication,
    SessionAuthentication,
)
from rest_framework.permissions import IsAuthenticated

from gatheros_subscription.lot_api_permissions import MultiLotsAllowed
from gatheros_subscription.models import Subscription
from gatheros_subscription.serializers import (
    Lot,
    LotSerializer,
    SubscriptionSerializer,
)


class RestrictionViewMixin:
    authentication_classes = (SessionAuthentication, BasicAuthentication)


class LotViewSet(RestrictionViewMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Lot.objects.all().order_by('name')
    serializer_class = LotSerializer

    def get_queryset(self):
        user = self.request.user

        org_pks = [
            m.organization.pk
            for m in user.person.members.filter(active=True)
        ]

        queryset = super().get_queryset()
        return queryset.filter(event__organization__in=org_pks)

    def check_permissions(self, request):
        """
        Check if the request should be permitted.
        Raises an appropriate exception if the request is not permitted.

        Special case: Viewset does not allow object creation without
        the multi-lot flag enabled.
        """

        if request.method == "POST":
            self.permission_classes = (IsAuthenticated, MultiLotsAllowed)
        else:
            self.permission_classes = (IsAuthenticated,)

        for permission in self.get_permissions():
            if not permission.has_permission(request, self):
                self.permission_denied(
                    request, message=getattr(permission, 'message', None)
                )


class SubscriptionListViewSet(RestrictionViewMixin,
                              generics.ListAPIView):
    """
    API endpoint for the subscription list view
    """
    serializer_class = SubscriptionSerializer

    def get_queryset(self):
        event_pk = self.kwargs['event_pk']

        return Subscription.objects.filter(
            event_id=event_pk,
            completed=True,
        )


