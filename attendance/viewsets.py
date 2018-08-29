import re
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.authentication import (
    BasicAuthentication,
    SessionAuthentication,
)
from rest_framework.permissions import IsAuthenticated

from attendance import models, serializers
from gatheros_subscription.models import Subscription


class RestrictionViewMixin(object):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)


def search_subscriptions(service, queryset, search_criteria):
    if not search_criteria:
        return queryset

    # Fetch by event count
    if search_criteria.isdigit():
        queryset = queryset.filter(event_count=int(search_criteria))
        if queryset.count() > 0:
            return queryset

    # Filter by email
    email_queryset = queryset.filter(
        person__email__icontains=search_criteria
    )
    if email_queryset.count() > 0:
        return email_queryset

    # Fetch by subscription code
    code_queryset = queryset.filter(code=search_criteria)
    if code_queryset.count() > 0:
        return code_queryset

    # Fetch by CPF
    cpf_cnpj_criteria = re.sub('\.', '', search_criteria)
    cpf_cnpj_criteria = re.sub('/', '', cpf_cnpj_criteria)
    cpf_cnpj_criteria = re.sub('-', '', cpf_cnpj_criteria)

    cpf_queryset = queryset.filter(person__cpf=cpf_cnpj_criteria)
    if cpf_queryset.count() > 0:
        return cpf_queryset

    cnpf_query = queryset.filter(
        person__institution_cnpj=cpf_cnpj_criteria
    )
    if cnpf_query.count() > 0:
        return cnpf_query

    # Filter by name
    queryset = queryset.filter(person__name__icontains=search_criteria)

    return queryset


class AttendanceServiceViewSet(RestrictionViewMixin, viewsets.ModelViewSet):
    """
         Essa view é responsavel por retornar o usuário, se membro da
         organização, poderá acessar os serviços opcionais de todos os seus
         eventos
    """
    queryset = models.AttendanceService.objects.all().order_by('name')
    serializer_class = serializers.AttendanceServiceSerializer

    def get_queryset(self):
        user = self.request.user

        org_pks = [
            m.organization.pk
            for m in user.person.members.filter(active=True)
        ]

        queryset = super().get_queryset()
        return queryset.filter(event__organization_id__in=org_pks)


class SubscriptionAttendanceViewSet(RestrictionViewMixin,
                                    viewsets.ModelViewSet):

    queryset = Subscription.objects.all().order_by('person__name')
    serializer_class = serializers.SubscriptionAttendanceSerializer

    def get_queryset(self):
        user = self.request.user

        org_pks = [
            m.organization.pk
            for m in user.person.members.filter(active=True)
        ]

        queryset = super().get_queryset()
        queryset = queryset.filter(
            completed=True,
            test_subscription=False,
            event__organization_id__in=org_pks
        )

        # Neste caso, inscrições são atreladas a algum Atendimento e,
        # por sua vez, ao evento.
        service = models.AttendanceService.objects.get(
            pk=self.kwargs.get('service_pk')
        )
        queryset = queryset.filter(event=service.event)

        # filter lot category
        lot_category_pks = [
            lot_cat_filter.lot_category.pk
            for lot_cat_filter in service.lot_category_filters.all()
        ]

        if lot_category_pks:
            queryset = queryset.filter(lot__category_id__in=lot_category_pks)

        checkin_param = self.request.query_params.get('checkedin')
        if checkin_param is not None:
            if checkin_param == 'true':
                # queryset = queryset.annotate(num_checkins=Count('checkins'))
                queryset = queryset.filter(
                    checkins__isnull=False,
                    checkins__checkout__isnull=True
                )
            elif checkin_param == 'false':
                queryset = queryset.filter(
                    Q(checkins__isnull=True) |
                    Q(checkins__checkout__isnull=False)
                )

        search_criteria = self.request.query_params.get('search')
        if search_criteria:
            queryset = search_subscriptions(service, queryset, search_criteria)

        return queryset

    def get_serializer(self, *args, **kwargs):
        serializer = super().get_serializer(*args, **kwargs)

        return serializer


class CheckinViewSet(RestrictionViewMixin, viewsets.ModelViewSet):
    queryset = models.Checkin.objects.all()
    serializer_class = serializers.CheckinSerializer

    def get_queryset(self):
        user = self.request.user

        org_pks = [
            m.organization.pk
            for m in user.person.members.filter(active=True)
        ]

        queryset = super().get_queryset()
        return queryset.filter(
            attendance_service__event__organization_id__in=org_pks
        )


class CheckoutViewSet(RestrictionViewMixin, viewsets.ModelViewSet):
    queryset = models.Checkout.objects.all()
    serializer_class = serializers.CheckoutSerializer

    def get_queryset(self):
        user = self.request.user

        org_pks = [
            m.organization.pk
            for m in user.person.members.filter(active=True)
        ]

        queryset = super().get_queryset()
        return queryset.filter(
            attendance_service__event__organization_id__in=org_pks
        )
