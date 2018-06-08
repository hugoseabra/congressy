from datetime import datetime
from decimal import Decimal

from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import DetailView
from core.views.mixins import TemplateNameableMixin
from gatheros_event.helpers.account import update_account
from gatheros_event.models import Event
from gatheros_event.models import Info, Organization
from gatheros_event.views.mixins import AccountMixin
from gatheros_subscription.models import Subscription, EventSurvey
from payment.models import Transaction


class EventPanelView(TemplateNameableMixin, AccountMixin, DetailView):
    model = Event
    # template_name = 'gatheros_event/event/panel.html'
    template_name = 'event/panel.html'
    permission_denied_url = reverse_lazy('event:event-list')
    object = None

    def post(self, request, *args, **kwargs):
        id_row = request.POST.get('id_row')
        row_name = id_row[4:]
        val = True
        if id_row:
            if id_row[:3] == 'add':
                val = True

            elif id_row[:3] == 'del':
                val = False

            if row_name == 'checkin':
                self.event.has_checkin = val

            elif row_name == 'extra_activities':
                self.event.has_extra_activities = val

            elif row_name == 'certificate':
                self.event.has_certificate = val

            elif row_name == 'optionals':
                self.event.has_optionals = val

            self.event.save()

        return HttpResponse(status=201)

    def pre_dispatch(self, request):
        self.object = self.get_object()

        if self.object:
            update_account(
                request=self.request,
                organization=self.object.organization,
                force=True
            )

        return super().pre_dispatch(request)

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.event = get_object_or_404(Event, pk=self.kwargs.get('pk'))

        # return redirect(reverse('subscription:subscription-list', kwargs={
        #     'event_pk': self.object.pk
        # }))

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.event = self.get_event(**kwargs)
        context = super(EventPanelView, self).get_context_data(**kwargs)
        context['event'] = self.get_event(**kwargs)
        context['status'] = self._get_status()
        context['totals'] = self._get_payables()
        context['limit'] = self._get_limit()
        context['has_paid_lots'] = self.has_paid_lots()
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
        context['has_addons'] = self.has_addons()
        context['percent_attended'] = {
            'label': round(self.object.percent_attended),
            'number': str(self.object.percent_attended).replace(',', '.'),
        }
        context['report'] = self._get_report()
        context['full_banking'] = self._get_full_banking()
        context['has_survey_create']= self.has_survey_create()
        context['number_attendances'] = self.get_number_attendances()
        context['status_addons'] = self.get_status_addons()
        try:
            context['is_configured'] = self.event.work_config.is_configured
        except AttributeError:
            context['is_configured'] = False

        try:
            context['info'] = self.event.info
        except Info.DoesNotExist:
            pass


        return context

    def get_status_addons(self):
        has_services = False
        has_products = False
        for lotcategory in self.event.lot_categories.all():
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
                event=self.get_event(),
            ).count()

        except Subscription.DoesNotExist:
            return 0

    def get_event(self, **kwargs):
        return get_object_or_404(Event, pk=self.kwargs.get('pk'))

    def has_addons(self):
        has_addons = {
            'extra_activities': self.event.has_extra_activities,
            'optionals': self.event.has_optionals,
            'checkin': self.event.has_checkin,
            'certificate': self.event.has_certificate,
            'survey': self.event.has_survey,
        }

        return has_addons

    def has_paid_lots(self):
        """ Retorna se evento possui algum lote pago. """
        for lot in self.event.lots.all():

            if lot.price is None:
                continue

            if lot.price > 0 and lot.active:
                return True

        return False



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
        return self.event.get_report()

    def _get_limit(self):
        return self.event.limit

    def _get_total_subscriptions(self):
        return self.event.subscriptions.filter(
            completed=True,
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
                Q(subscription__event=self.event) &
                Q(subscription__completed=True) &
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
                event=self.event,
            ).exclude(
                status=Subscription.CANCELED_STATUS
            ).count()

        return pending

    def has_survey_create(self):
        event_survey_qs = EventSurvey.objects.filter(event=self.event)

        for event_survey in event_survey_qs:
            survey = event_survey.survey
            has_questions = survey.questions.count() > 0
            has_lots = survey.lots.count() > 0
            if has_questions and has_lots:
                return True

        return False
