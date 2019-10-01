from rest_framework import permissions, status
from rest_framework.authentication import (
    BasicAuthentication,
    SessionAuthentication,
    TokenAuthentication,
)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from gatheros_event.models import Person
from payment.models import Benefactor
from payment.serializers import (
    BenefactorSerializer,
)


class RestrictionViewMixin(object):
    authentication_classes = (
        SessionAuthentication,
        BasicAuthentication,
        TokenAuthentication,
    )
    permission_classes = (permissions.IsAuthenticated,)


class BenefactorViewSet(RestrictionViewMixin, ModelViewSet):
    serializer_class = BenefactorSerializer

    def get_queryset(self):

        queryset = Benefactor.objects.get_queryset()

        user = self.request.user

        if hasattr(user, 'person') is False:
            return queryset.none()

        person = user.person

        return queryset.filter(beneficiary_id=person.pk)
