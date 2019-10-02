from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from payment.models import Transaction, TransactionStatus
from payment.serializers import (
    TransactionSerializer,
    TransactionStatusSerializer,
)
from .mixins import RestrictionViewMixin


class TransactionReadOnlyViewSet(RestrictionViewMixin, ReadOnlyModelViewSet):
    serializer_class = TransactionSerializer

    def get_organizer_pks(self):
        user = self.request.user

        if hasattr(user, 'person') is False:
            return []

        return [
            m.organization_id
            for m in user.person.members.filter(active=True)
        ]

    def get_queryset(self):
        # Fetch transactions for user in request
        user_transactions = self.get_user_transactions()

        # Fetch transactions for subscriptions in the user in the requests
        # organization
        organizations_transactions = self.get_organizations_transactions()

        # Merging querysets
        qs = user_transactions | organizations_transactions

        if 'event' in self.request.query_params:
            event_pk = self.request.query_params.get('event')
            if event_pk:
                qs = qs.filter(
                    subscription__event_id=event_pk,
                )

        if 'subscription' in self.request.query_params:
            subscription_pk = self.request.query_params.get('subscription')
            if subscription_pk:
                qs = qs.filter(
                    subscription_id=subscription_pk,
                )

        return qs.order_by("date_created")

    def get_user_transactions(self):
        return Transaction.objects.filter(
            subscription__person__user_id=self.request.user.pk,
        )

    def get_organizations_transactions(self):
        return Transaction.objects.filter(
            subscription__event__organization_id__in=self.get_organizer_pks(),
        )


class TransactionStatusListView(RestrictionViewMixin, ListAPIView):
    serializer_class = TransactionStatusSerializer

    def get_organizer_pks(self):
        user = self.request.user

        if hasattr(user, 'person') is False:
            return []

        return [
            m.organization_id
            for m in user.person.members.filter(active=True)
        ]

    def owns_transaction(self, transaction_pk):

        user = self.request.user

        # Request user owns transaction
        try:
            Transaction.objects.get(
                pk=transaction_pk,
                subscription__person__user_id=user.pk,
            )

            return True

        except Transaction.DoesNotExist:
            pass

        for org_pk in self.get_organizer_pks():
            try:
                Transaction.objects.get(
                    pk=transaction_pk,
                    subscription__event__organization_id=org_pk
                )

                return True

            except Transaction.DoesNotExist:
                pass

        return False

    def get_queryset(self):
        return TransactionStatus.objects.filter(
            transaction_id=self.request.query_params.get('pk'),
        )

    def list(self, request, *args, **kwargs):

        if not self.owns_transaction(self.request.query_params.get('pk')):
            content = {
                'detail': 'unauthorized'
            }

            return Response(content, status=status.HTTP_401_UNAUTHORIZED)

        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
