from rest_framework import viewsets, views
from rest_framework.authentication import (
    BasicAuthentication,
    SessionAuthentication,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
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


class ServiceViewSet(RestrictionViewMixin, views.APIView):
        """
        A custom endpoint for GET request.
        """

        def get(self, *args, **kwargs):
            """
            Return a hardcoded response.
            """

            return Response({"success": True, "content": "Hello World!"})



class SubscriptionServiceViewSet(viewsets.ModelViewSet):
    """
        API endpoint that allows users to be viewed or edited.
    """
    queryset = models.SubscriptionService.objects.all()
    serializer_class = serializers.SubscriptionServiceSerializer
