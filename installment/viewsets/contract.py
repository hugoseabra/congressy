from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from installment.models import Contract
from installment.serializers import ContractSerializer
from .mixins import RestrictionViewMixin


class ContractViewSet(RestrictionViewMixin, ModelViewSet):
    serializer_class = ContractSerializer

    def get_queryset(self):

        user = self.request.user

        if 'mode' in self.request.query_params:
            mode = self.request.query_params.get('mode')

            if mode == 'organizer':
                org_pks = [
                    m.organization.pk
                    for m in user.person.members.filter(active=True)
                ]

                return Contract.objects.filter(
                    subscription__event__organization__in=org_pks
                )

        if not hasattr(user, 'person'):
            return Contract.objects.none()

        person = self.request.user.person

        return Contract.objects.filter(
            subscription__person_id=str(person.pk)
        )

    def list(self, request, *args, **kwargs):

        user = self.request.user

        org_pks = [
            m.organization.pk
            for m in user.person.members.filter(active=True)
        ]

        queryset = Contract.objects.filter(
            subscription__event__organization__in=org_pks
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):

        user = self.request.user

        org_pks = [
            m.organization.pk
            for m in user.person.members.filter(active=True)
        ]

        queryset = Contract.objects.filter(
            subscription__event__organization__in=org_pks
        )

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
                'Expected view %s to be called with a URL keyword argument '
                'named "%s". Fix your URL conf, or set the `.lookup_field` '
                'attribute on the view correctly.' %
                (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        instance = obj
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
