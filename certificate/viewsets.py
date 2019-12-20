from rest_framework import viewsets

from certificate import models, serializers
from core.viewsets import AuthenticatedViewSetMixin


class CertificateViewSet(AuthenticatedViewSetMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = models.Certificate.objects.all().order_by('event__name')
    serializer_class = serializers.CertificateSerializer
