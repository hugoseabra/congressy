from datetime import datetime
from decimal import Decimal

from django.db.models import Q
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import DetailView

from core.views.mixins import TemplateNameableMixin
from gatheros_event.event_specifications import (
    EventSubscribable,
)
from gatheros_event.helpers.event_business import is_paid_event
from gatheros_event.models import Event, Info, Organization
from gatheros_event.views.mixins import AccountMixin, EventDraftStateMixin
from gatheros_subscription.models import Subscription, EventSurvey, Lot
from payment.models import Transaction


class EventPanelView(EventDraftStateMixin,
                     TemplateNameableMixin,
                     AccountMixin,
                     DetailView, ):
    model = Event
    template_name = 'event/panel.html'
    permission_denied_url = reverse_lazy('event:event-list')
    object = None

    def post(self, request, *args, **kwargs):

        self.object = self.get_object()
        feature_config = self.object.feature_configuration
        feature_management = self.object.feature_management

        id_row = request.POST.get('id_row')
        row_name = id_row[4:]
        val = True

        if id_row:

            if id_row[:3] == 'add':
                val = True

            elif id_row[:3] == 'del':
                val = False

            if row_name == 'checkin':
                if feature_config.feature_checkin:
                    feature_management.checkin = val
                    feature_management.save()
                    return HttpResponse(status=201)
                else:
                    return HttpResponse("Evento não possui essa funcionalidade",
                                        status=403)

            elif row_name == 'extra_activities':
                if feature_config.feature_services:
                    feature_management.services = val
                    feature_management.save()
                    return HttpResponse(status=201)
                else:
                    return HttpResponse("Evento não possui essa funcionalidade",
                                        status=403)

            elif row_name == 'certificate':
                if feature_config.feature_certificate:
                    feature_management.certificate = val
                    feature_management.save()
                    return HttpResponse(status=201)
                else:
                    return HttpResponse("Evento não possui essa funcionalidade",
                                        status=403)

            elif row_name == 'optionals':
                if feature_config.feature_products:
                    feature_management.products = val
                    feature_management.save()
                    return HttpResponse(status=201)
                else:
                    return HttpResponse("Evento não possui essa funcionalidade",
                                        status=403)

            elif row_name == 'survey':
                if feature_config.feature_survey:
                    feature_management.survey = val
                    feature_management.save()
                    return HttpResponse(status=201)
                else:
                    return HttpResponse("Evento não possui essa funcionalidade",
                                        status=403)

        return HttpResponse(status=200)

    def get_context_data(self, **kwargs):

        kwargs.update({'event': self.object})

        context = super(EventPanelView, self).get_context_data(**kwargs)

        context['event'] = self.object
        context['feature_config'] = self.object.feature_configuration
        context['feature_management'] = self.object.feature_management
        context['status'] = self._get_status()
        context['totals'] = self._get_payables()
        context['limit'] = self._get_limit()
        context['event_is_subscribable'] = EventSubscribable() \
            .is_satisfied_by(self.object)
        context['event_is_payable'] = is_paid_event(self.object)
        context['all_lots'] = self.all_lots_status()
        context['gender'] = self._get_gender()
        context['pending'] = self._get_number_pending()
        context['has_inside_bar'] = True
        context['active'] = 'panel'
        context['total_subscriptions'] = self._get_total_subscriptions()
        context['can_transfer'] = self._can_transfer
        context['can_change'] = self._can_change
        context['can_delete'] = self._can_delete
        context['can_view_lots'] = self._can_view_lots
        context['can_manage_subscriptions'] = self.can_manage_subscriptions
        context['percent_attended'] = {
            'label': round(self.object.percent_attended),
            'number': str(self.object.percent_attended).replace(',', '.'),
        }
        context['report'] = self._get_report()
        context['full_banking'] = self._get_full_banking()
        context['has_survey_create'] = self.has_survey_create()
        context['number_attendances'] = self.get_number_attendances()
        context['status_addons'] = self.get_status_addons()
        context['event_is_full'] = self.event_is_full()
        context['is_paid_event'] = is_paid_event(self.object)

        try:
            context['is_configured'] = self.object.work_config.is_configured
        except AttributeError:
            context['is_configured'] = False

        try:
            context['info'] = self.object.info
        except Info.DoesNotExist:
            pass

        try:
            context['ready_certificate'] = self.object.certificate.is_ready
        except AttributeError:
            context['ready_certificate'] = False

        context.update(
            EventDraftStateMixin().get_event_state_context_data(self.object))

        return context

    def all_lots_status(self):
        lots = {
            'running': [],
            'finished': [],
            'notstarted': []
        }
        for lot in self.object.lots.all():
            lot_istance = {
                'name': lot.name,
                'limit': lot.limit,
                'number_subscription': lot.subscriptions.filter(
                    completed=True, test_subscription=False
                ).exclude(
                    status='canceled'
                ).count(),
                'percent_completed': lot.percent_completed
            }
            if lot.status == Lot.LOT_STATUS_RUNNING:
                lots['running'].append(lot_istance)

            elif lot.status == Lot.LOT_STATUS_NOT_STARTED:
                lots['notstarted'].append(lot_istance)

            elif lot.status == Lot.LOT_STATUS_FINISHED:
                lots['finished'].append(lot_istance)

        return lots

    def get_status_addons(self):
        has_services = False
        has_products = False
        for lotcategory in self.object.lot_categories.all():
            if lotcategory.service_optionals.count():
                has_services = True

            if lotcategory.product_optionals.count():
                has_products = True

        status_addons = {
            'services': has_services,
            'products': has_products
        }

        return status_addons

    def get_number_attendances(self):
        try:
            return Subscription.objects.filter(
                attended=True,
                event=self.object,
            ).count()

        except Subscription.DoesNotExist:
            return 0

    def _get_full_banking(self):

        if not self.organization:
            return False

        banking_required_fields = ['bank_code', 'agency', 'account',
            'cnpj_ou_cpf', 'account_type']

        for field in Organization._meta.get_fields():

            for required_field in banking_required_fields:

                if field.name == required_field:

                    if not getattr(self.organization, field.name):
                        return False

        return True

    def _get_gender(self):
        return self.object.get_report()

    def _get_limit(self):
        return self.object.limit

    def _get_total_subscriptions(self):
        return self.object.subscriptions.filter(
            completed=True, test_subscription=False
        ).exclude(
            status=Subscription.CANCELED_STATUS
        ).count()

    def can_access(self):
        event = self.get_object()
        return event.organization == self.organization

    def _can_transfer(self):
        """ Verifica se usuário pode transferir este evento. """
        return self.is_organization_admin

    def _can_change(self):
        """ Verifica se usuário pode alterar o evento. """
        return self.request.user.has_perm(
            'gatheros_event.change_event',
            self.object
        )

    def _can_delete(self):
        """ Verifica se usuário pode excluir o evento. """
        return self.object.is_deletable() and self.request.user.has_perm(
            'gatheros_event.delete_event',
            self.object
        )

    def _can_view_lots(self):
        """ Verifica se usuário pode visualizar lotes. """
        subscription_by_lots = \
            self.object.subscription_type == Event.SUBSCRIPTION_BY_LOTS

        can_manage = self.request.user.has_perm(
            'gatheros_event.view_lots',
            self.object
        )

        return subscription_by_lots and can_manage

    def can_manage_subscriptions(self):
        """ Verifica se usuário pode gerenciar inscrições. """
        return self.request.user.has_perm(
            'gatheros_subscription.can_manage_subscriptions',
            self.object
        )

    def _get_status(self):
        """ Resgata o status. """
        now = datetime.now()
        event = self.object
        remaining = self._get_remaining_datetime()
        remaining_str = self._get_remaining_days(date=remaining)

        result = {
            'published': event.published,
        }

        future = event.date_start > now
        running = event.date_start <= now <= event.date_end
        finished = now >= event.date_end

        if future:
            result.update({
                'status': 'future',
                'remaining': remaining_str,
            })

        elif running:
            result.update({
                'status': 'running',
            })

        elif finished:
            result.update({
                'status': 'finished' if event.published else 'expired',
            })

        return result

    def _get_remaining_datetime(self):
        """ Resgata diferença de tempo que falta para o evento finalizar. """
        now = datetime.now()
        return self.object.date_start - now

    def _get_remaining_days(self, date=None):
        """ Resgata tempo que falta para o evento finalizar em dias. """
        now = datetime.now()

        if not date:
            date = self._get_remaining_datetime()

        remaining = ''

        days = date.days
        if days > 0:
            remaining += str(date.days) + 'dias '

        remaining += str(int(date.seconds / 3600)) + 'h '
        remaining += str(60 - now.minute) + 'm'

        return remaining

    def _get_report(self):
        """ Resgata informações gerais do evento. """
        return self.object.get_report()

    def _get_payables(self):

        totals = {
            'total': Decimal(0.00),
            'pending': Decimal(0.00),
            'paid': Decimal(0.00),
        }

        transactions = \
            Transaction.objects.filter(
                Q(subscription__event=self.object) &
                Q(subscription__completed=True) &
                Q(subscription__test_subscription=False) &
                (
                        Q(status=Transaction.PAID) |
                        Q(status=Transaction.WAITING_PAYMENT)
                )
            ).exclude(subscription__status=Subscription.CANCELED_STATUS)

        for transaction in transactions:
            totals['total'] += transaction.liquid_amount or Decimal(0.00)

            if transaction.paid:
                totals['paid'] += transaction.liquid_amount or Decimal(0.00)

            if transaction.pending:
                totals['pending'] += transaction.liquid_amount or Decimal(0.00)

        return totals

    def _get_number_pending(self):

        pending = \
            Subscription.objects.filter(
                status=Subscription.AWAITING_STATUS,
                completed=True,
                test_subscription=False,
                event=self.object,
            ).exclude(
                status=Subscription.CANCELED_STATUS
            ).count()

        return pending

    def has_survey_create(self):
        event_survey_qs = EventSurvey.objects.filter(event=self.object)

        for event_survey in event_survey_qs:
            survey = event_survey.survey
            has_questions = survey.questions.count() > 0
            has_lots = survey.event.lots.count() > 0
            if has_questions and has_lots:
                return True

        return False

    def event_is_full(self):
        if self.object.expected_subscriptions and \
                self.object.expected_subscriptions > 0:

            total_subscriptions_event = 0
            for lot in self.object.lots.all():
                total_subscriptions_event += lot.subscriptions.filter(
                    completed=True, test_subscription=False
                ).exclude(
                    status='canceled'
                ).count()
            return total_subscriptions_event >= self.object.expected_subscriptions

        else:
            return False
