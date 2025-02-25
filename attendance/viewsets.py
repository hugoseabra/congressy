import re
from datetime import datetime

from django.db.models import Q
from django.http import HttpResponse
from django.utils.text import slugify
from rest_framework import viewsets, status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from attendance import models, serializers
from attendance.helpers.async_exporter_helpers import \
    AttendanceServiceAsyncExporter
from attendance.models import AttendanceService
from attendance.tasks import async_attendance_exporter_task
from core.viewsets import AuthenticatedViewSetMixin
from gatheros_subscription.models import Subscription


def search_subscriptions(queryset, search_criteria):
    if not search_criteria:
        return queryset.none()

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
    code_queryset = queryset.filter(code=str(search_criteria).upper())
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
    queryset = queryset.filter(
        person__name__icontains=str(search_criteria).lower()
    )

    return queryset


class AttendanceServiceViewSet(AuthenticatedViewSetMixin,
                               viewsets.ModelViewSet):
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


class AttendancePageSizer(LimitOffsetPagination):
    default_limit = 6


class SubscriptionAttendanceViewSet(AuthenticatedViewSetMixin,
                                    viewsets.ModelViewSet):
    queryset = Subscription.objects.all().order_by('person__name')
    serializer_class = serializers.SubscriptionAttendanceSerializer
    pagination_class = AttendancePageSizer

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
            event__organization_id__in=org_pks,
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

        if 'search' in self.request.query_params:
            search_criteria = self.request.query_params.get('search')
            queryset = search_subscriptions(queryset, search_criteria)

        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['attendance_service_pk'] = self.kwargs.get('service_pk')
        return context

    def create(self, request, *args, **kwargs):
        content = {
            'status': 'request is not allowed.'
        }
        return Response(content, status=405)

    def update(self, request, *args, **kwargs):
        content = {
            'status': 'request is not allowed.'
        }
        return Response(content, status=405)

    def partial_update(self, request, *args, **kwargs):
        content = {
            'status': 'request is not allowed.'
        }
        return Response(content, status=405)

    def destroy(self, request, *args, **kwargs):
        content = {
            'status': 'request is not allowed.'
        }
        return Response(content, status=405)


class CheckinViewSet(AuthenticatedViewSetMixin, viewsets.ModelViewSet):
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

    def list(self, request, *args, **kwargs):
        content = {
            'status': 'request is not allowed.'
        }
        return Response(content, status=405)


class CheckoutViewSet(AuthenticatedViewSetMixin, viewsets.ModelViewSet):
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
            checkin__attendance_service__event__organization_id__in=org_pks
        )

    def list(self, request, *args, **kwargs):
        content = {
            'status': 'request is not allowed.'
        }
        return Response(content, status=405)


class AttendanceServiceExporterViewSet(AuthenticatedViewSetMixin, APIView):

    # @TODO Implement OrganizerOnly permission
    # @TODO Implement FeatureFlag permission

    def post(self, request, *args, **kwargs):
        service_pk = kwargs.get('service_pk')

        if not service_pk:
            return Response({'error: missing pk'},
                            status=status.HTTP_400_BAD_REQUEST)

        service = AttendanceService.objects.get(pk=service_pk)

        exporter = AttendanceServiceAsyncExporter(service)

        if exporter.has_export_lock():
            return Response(status=status.HTTP_204_NO_CONTENT)

        async_attendance_exporter_task.delay(event_pk=service.event_id,
                                             service_pk=service.pk)

        return HttpResponse(status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):

        service_pk = kwargs.get('service_pk')

        if not service_pk:
            return Response({'error: missing pk'},
                            status=status.HTTP_400_BAD_REQUEST)

        service = AttendanceService.objects.get(pk=service_pk)

        exporter = AttendanceServiceAsyncExporter(service)

        if exporter.has_export_lock():
            return Response(status=status.HTTP_204_NO_CONTENT)

        if not exporter.has_existing_export_files():
            return Response(status=status.HTTP_404_NOT_FOUND)

        # Criando resposta http com arquivo de download
        # Reading file
        file_name = exporter.get_export_file_path()
        output = open(file_name, mode='rb').read()
        name = "%s_%s_%s.xlsx" % (
            service.event.slug,
            slugify(service.name),
            datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        )

        response = HttpResponse(
            output,
            content_type="application/vnd.ms-excel"
        )

        response['Content-Disposition'] = 'attachment; filename=%s' % name

        return response
