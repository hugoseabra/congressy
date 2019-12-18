from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from certificate import models, serializers


class RestrictionViewMixin(object):
    permission_classes = (IsAuthenticated,)


class CertificateViewSet(RestrictionViewMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = models.Certificate.objects.all().order_by('event__name')
    serializer_class = serializers.CertificateSerializer
