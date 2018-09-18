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


class EventMixin(TemplateNameableMixin):
    current_event = None

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
        context['lots'] = event_state.get_public_lots()
        context['available_lots'] = event_state.get_public_lots()
        context['has_available_lots'] = event_state.has_available_lots()
        context['has_paid_lots'] = event_state.has_paid_lots()

        context['paid_lots'] = event_state.get_all_lots()
        context['private_lots'] = event_state.get_private_lots()
        context['is_private_event'] = event_state.is_private_event()
        context['subscription_enabled'] = event_state.subscription_enabled()
        context['subscription_finished'] = event_state.subscription_finished()

        context['has_coupon'] = event_state.has_coupon()
        context['has_configured_bank_account'] = \
            event_state.bank_account_configured

        context['has_active_bank_account'] = \
            event_state.active_bank_account_configured

        context['google_maps_api_key'] = settings.GOOGLE_MAPS_API_KEY
        context['custom_service_tag'] = event_state.custom_service_tag

        return context


class SubscriptionFormMixin(EventMixin):
    form_class = PersonForm
    initial = {}
    current_subscription = None

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

        try:
            subscription = Subscription.objects.get(
                person=person,
                event=self.current_event.event,
            )
            subscription.is_new = False

        except Subscription.DoesNotExist:

            lots = self.current_event.get_all_lots()
            if lots:
                lot = lots[0]
            else:
                lot = self.current_event.event.lots.first()

            if not lot:
                lot = Lot(
                    event=self.current_event.event,
                    date_start=datetime.now(),
                    date_end=datetime.now() + timedelta(days=2),
                    name='invalid',
                )

            subscription = Subscription(
                person=person,
                event=self.current_event.event,
                completed=False,
                created_by=user.pk,
                lot=lot,
            )
            subscription.is_new = True

        return subscription

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_config'] = self.current_event.form_config

        if 'form' not in kwargs:
            context['form'] = self.get_form()

        person = self.current_subscription.person
        sub = self.current_subscription.subscription
        sub_lot = self.current_subscription.lot

        context['person'] = person

        if person:
            context['subscription'] = sub
            context['is_subscribed'] = sub is not None
            context['lot_still_available'] = \
                sub_lot and self.current_event.is_lot_running(sub_lot)
        else:
            context['is_subscribed'] = sub is not None

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


class SelectLotMixin(SubscriptionFormMixin):
    def get_selected_lot(self):
        if 'lot_pk' in self.request.session and self.request.session['lot_pk']:
            # se PK de lote existe na sessão, prioriza-lo pois ele pode
            # ser um lote vindo do primeiro passo.
            try:
                self.selected_lot = \
                    Lot.objects.get(pk=self.request.session['lot_pk'])

            except Lot.DoesNotExist:
                pass

        else:
            # se não há PK de lote, vamos verificar se usuário já possui
            # inscrição
            sub_lot = self.current_subscription.lot

            if sub_lot:
                self.selected_lot = sub_lot

        self.request.session['lot_pk'] = self.selected_lot.pk
        return self.selected_lot
