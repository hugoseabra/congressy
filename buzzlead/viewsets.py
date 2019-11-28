from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.authentication import (
    SessionAuthentication,
    BasicAuthentication,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from buzzlead.serializers import BuzzLeadCampaignSerializer
from project.token_authentication import ExpiringTokenAuthentication


class RestrictionViewMixin(object):
    authentication_classes = (SessionAuthentication,
                              BasicAuthentication,
                              ExpiringTokenAuthentication)
    permission_classes = (IsAuthenticated,)


class BuzzLeadCampaignViewSet(RestrictionViewMixin, viewsets.ModelViewSet):
    """
        Essa view é responsavel por retornar o usuário, se membro da
        organização, poderá acessar os produtos opcionais de todos os seus
        eventos
    """
    queryset = BuzzLeadCampaignSerializer.Meta.model.objects.all()
    serializer_class = BuzzLeadCampaignSerializer

    def get_queryset(self):
        user = self.request.user

        queryset = super().get_queryset()
        if user.email == settings.BUZZLEAD_MANAGER_EMAIL:
            return queryset

        org_pks = [
            m.organization_id
            for m in user.person.members.filter(active=True)
        ]

        return queryset.filter(
            event__organization_id__in=org_pks
        )

    def list(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
