from rest_framework.viewsets import ModelViewSet

from core.viewsets import AuthenticatedViewSetMixin
from payment.models import Benefactor
from payment.serializers import BenefactorSerializer


class BenefactorViewSet(AuthenticatedViewSetMixin, ModelViewSet):
    serializer_class = BenefactorSerializer

    def get_queryset(self):
        queryset = Benefactor.objects.get_queryset()

        user = self.request.user

        if hasattr(user, 'person') is False:
            return queryset.none()

        person = user.person

        return queryset.filter(beneficiary_id=person.pk)
