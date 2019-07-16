"""
    Mixins usados no módulo de hotsite.
"""
from datetime import datetime, timedelta
from django.conf import settings
from django.shortcuts import get_object_or_404

from core.views.mixins import TemplateNameableMixin
from gatheros_event.forms import PersonForm
from gatheros_event.models import Event, Person
from gatheros_subscription.models import Lot, Subscription
from hotsite.state import CurrentEventState, CurrentSubscriptionState
from gatheros_event.helpers.event_business import is_paid_event
from gatheros_event.models import Event, Info
from gatheros_subscription.models import FormConfig, Subscription
from ticket.models import Lot, Ticket

class EventMixin(TemplateNameableMixin):

    def __init__(self, *args, **kwargs):
        self.current_event = None
        super().__init__(*args, **kwargs)

    def pre_dispatch(self):
        slug = self.kwargs.get('slug')
        event = get_object_or_404(Event, slug=slug)
        self.current_event = CurrentEventState(event=event)

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug')

        if not slug:
            raise Exception('Nenhum slug encontrado.')

        self.pre_dispatch()

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        event_state = self.current_event
        config = event_state.form_config

        if config and is_paid_event(self.current_event.event):
            config.email = True
            config.phone = True
            config.city = True

            config.cpf = config.CPF_REQUIRED
            config.birth_date = config.BIRTH_DATE_REQUIRED
            config.address = config.ADDRESS_SHOW

        context['config'] = config

        context['event'] = event_state.event
        context['info'] = event_state.info
        context['period'] = event_state.period
        context['public_tickets'] = event_state.get_public_tickets()
        context['available_tickets'] = event_state.get_available_tickets()
        context['has_available_tickets'] = event_state.has_available_tickets()
        context['has_paid_tickets'] = event_state.has_paid_tickets()

        context['paid_tickets'] = event_state.get_paid_tickets()
        context['private_tickets'] = event_state.get_private_tickets()
        context['is_private_event'] = event_state.is_private_event()
        context['subscription_enabled'] = event_state.subscription_enabled()
        context['subscription_finished'] = \
            event_state.has_available_tickets() is False

        context['has_coupon'] = event_state.has_coupon()
        context['has_configured_bank_account'] = \
            event_state.bank_account_configured

        context['has_active_bank_account'] = \
            event_state.active_bank_account_configured

        context['google_maps_api_key'] = settings.GOOGLE_MAPS_API_KEY
        context['custom_service_tag'] = event_state.custom_service_tag

        return context


class SubscriptionMixin(EventMixin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_subscription = None

    def pre_dispatch(self):
        super().pre_dispatch()

        self.current_subscription = CurrentSubscriptionState(
            subscription=self._get_subscription()
        )
    def _get_subscription(self):

        person = None
        user = self.request.user
        if hasattr(user, 'person'):
            person = user.person

        if not person:
            person = Person()
            person.brand_new = True
        else:
            person.brand_new = False

        try:
            subscription = Subscription.objects.get(
                person_id=person.pk,
                event_id=self.current_event.event.pk,
            )
            subscription.brand_new = False

        except Subscription.DoesNotExist:

            subscription = Subscription(
                person=person,
                event=self.current_event.event,
                completed=False,
                created_by=user.pk,
            )
            subscription.brand_new = True

        return subscription

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        person = self.current_subscription.person
        sub = self.current_subscription.subscription
        sub_lot = self.current_subscription.ticket_lot

        context['person'] = person

        if person:
            context['subscription'] = sub
            context['is_subscribed'] = sub is not None
            context['ticket_still_available'] = \
                sub_lot and sub_lot.running is True
        else:
            context['is_subscribed'] = sub is not None

        return context


class SubscriptionFormMixin(SubscriptionMixin):
    form_class = PersonForm
    initial = {}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_config'] = self.current_event.form_config

        if 'form' not in kwargs:
            context['form'] = self.get_form()

        return context

    def get_form_kwargs(self, **kwargs):
        """
        Returns the keyword arguments for instantiating the form.
        """
        if not kwargs:
            kwargs = {
                'initial': self.initial,
            }

        person = self.current_subscription.person
        if 'instance' not in kwargs and person:
            kwargs['instance'] = person

        if self.request.method in ('POST', 'PUT'):
            if 'data' not in kwargs:
                kwargs.update({'data': self.request.POST})

        return kwargs

    def get_form(self, **kwargs):
        return self.form_class(**self.get_form_kwargs(**kwargs))


class SelectTicketMixin(SubscriptionFormMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.select_ticket = None

    def pre_dispatch(self):
        super().pre_dispatch()

        if self.current_subscription.subscription.ticket_lot_id:
            # Se há ID do lote, há um ticket indiretamente relacionado.
            self.selected_ticket = \
                self.current_subscription.subscription.ticket

    def get_selected_ticket(self):
        if 'ticket_pk' in self.request.session and \
                self.request.session['ticket_pk']:
            # se PK de lote existe na sessão, prioriza-lo pois ele pode
            # ser o ingresso vindo do primeiro passo.
            try:
                self.selected_ticket = \
                    Ticket.objects.get(pk=self.request.session['ticket_pk'])

            except Ticket.DoesNotExist:
                pass

        # se não há PK de ticket na sessão, se a inscrição vigente existe
        # se há lote vinculado para encontrarmos o ticket
        elif self.current_subscription.subscription.ticket_lot_id:
            self.selected_ticket = self.current_subscription.ticket_lot

        if self.selected_ticket:
            self.request.session['ticket_pk'] = self.selected_ticket.pk

        return self.selected_ticket
