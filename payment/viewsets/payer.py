from rest_framework import permissions, status
from rest_framework.authentication import (
    BasicAuthentication,
    SessionAuthentication,
    TokenAuthentication,
)
from rest_framework.exceptions import NotFound
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from gatheros_event.models import Person
from gatheros_subscription.models import Subscription
from payment.models import Benefactor, Payer
from payment.serializers import (
    BenefactorSerializer,
    SubscriptionSerializer,
    PayerSerializer)


class RestrictionViewMixin(object):
    authentication_classes = (
        SessionAuthentication,
        BasicAuthentication,
        TokenAuthentication,
    )
    permission_classes = (permissions.IsAuthenticated,)


class PayerVieSet(RestrictionViewMixin, ModelViewSet):
    serializer_class = PayerSerializer

    def get_queryset(self):
        sub_pk = self.kwargs.get('subscription_pk')
        queryset = Payer.objects.get_queryset()

        if sub_pk:
            queryset = queryset.filter(subscription_id=sub_pk)

        return queryset

    def list(self, request, *args, **kwargs):
        content = {
            'detail': 'method not allowed'
        }

        return Response(content, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def create(self, request, *args, **kwargs):

        beneficiary_pk = request.data['beneficiary']
        if beneficiary_pk:

            try:
                Person.objects.get(pk=beneficiary_pk)

            except Person.DoesNotExist:
                return Response(
                    {
                        'detail': 'beneficiary not found'
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

        return super().create(request, *args, **kwargs)


class BenefactorSubscriptionsListView(RestrictionViewMixin, ListAPIView):
    serializer_class = SubscriptionSerializer

    def get_queryset(self):

        subscriptions = list()
        benefactor = None

        pk = self.kwargs['pk']
        if pk:
            try:
                benefactor = Benefactor.objects.get(pk=pk)
            except Benefactor.DoesNotExist:
                raise NotFound()

        payers = benefactor.payers.all()

        for payer in payers:
            subscriptions.append(payer.subscription.pk)

        return Subscription.objects.filter(pk__in=subscriptions, )


class BenefactorPersonListView(RestrictionViewMixin, ListAPIView):
    serializer_class = BenefactorSerializer

    def get_queryset(self):
        company_only = False

        if 'type' in self.request.query_params:
            is_company = self.request.query_params.get('type')
            company_only = is_company == 'cnpj'

        return Benefactor.objects.filter(
            is_company=company_only,
            beneficiary=self.kwargs.get('person_pk'),
        ).order_by('name')
