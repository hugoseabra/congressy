from rest_framework import viewsets
from rest_framework.authentication import (
    BasicAuthentication,
    SessionAuthentication,
)
from rest_framework.permissions import IsAuthenticated

from addon import models, serializers


class RestrictionViewMixin(object):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)


class ThemeViewSet(viewsets.ModelViewSet):
    """
        API endpoint that allows users to be viewed or edited.
    """
    queryset = models.Theme.objects.all().order_by('name')
    serializer_class = serializers.ThemeSerializer


class OptionalTypeViewSet(viewsets.ModelViewSet):
    """
        API endpoint that allows users to be viewed or edited.
    """
    queryset = models.OptionalType.objects.all().order_by('name')
    serializer_class = serializers.OptionalTypeSerializer


class ProductViewSet(viewsets.ModelViewSet):
    """
        API endpoint that allows users to be viewed or edited.
    """
    queryset = models.Product.objects.all().order_by('name')
    serializer_class = serializers.ProductSerializer


class SubscriptionProductViewSet(viewsets.ModelViewSet):
    """
        API endpoint that allows users to be viewed or edited.
    """
    queryset = models.SubscriptionProduct.objects.all()
    serializer_class = serializers.SubscriptionProductSerializer


class ServiceViewSet(viewsets.ModelViewSet):
    """
        API endpoint that allows users to be viewed or edited.
    """
    queryset = models.Service.objects.all().order_by('name')
    serializer_class = serializers.ServiceSerializer


class SubscriptionServiceViewSet(viewsets.ModelViewSet):
    """
        API endpoint that allows users to be viewed or edited.
    """
    queryset = models.SubscriptionService.objects.all()
    serializer_class = serializers.SubscriptionServiceSerializer
