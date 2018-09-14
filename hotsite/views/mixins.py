"""
    Mixins usados no módulo de hotsite.
"""

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, redirect
from django.views import generic

from core.views.mixins import TemplateNameableMixin
from gatheros_event.forms import PersonForm
from gatheros_event.models import Event, Info
from gatheros_subscription.models import FormConfig, Lot, Subscription
from payment.models import Transaction


class EventMixin(TemplateNameableMixin, generic.View):
    event = None
    info = None
    form_config = None
    period = None
    public_lots = []
    private_lots = []

    lot_statuses = {}

    bank_account_configured = True
    active_bank_account_configured = True

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug')

        if not slug:
            return redirect('https://congressy.com')

        self.get_event()

        return super().dispatch(request, *args, **kwargs)

    def get_event(self):
        if self.event:
            self.get_form_config()
            return self.event

        slug = self.kwargs.get('slug')
        self.event = get_object_or_404(Event, slug=slug)
        self.info = get_object_or_404(Info, event=self.event)
        self.period = self.event.get_period()

        organization = self.event.organization

        self.bank_account_configured = \
            organization.is_bank_account_configured()
        self.active_bank_account_configured = organization.active_recipient

        self.get_form_config()

        return self.event

    def get_form_config(self):
        if self.form_config is not None:
            return self.form_config

        try:
            self.form_config = self.event.form_config

        except (ObjectDoesNotExist, AttributeError):
            self.form_config = FormConfig()

        return self.form_config

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        config = self.form_config

        if config and self.has_paid_lots():
            config.email = True
            config.phone = True
            config.city = True

            config.cpf = config.CPF_REQUIRED
            config.birth_date = config.BIRTH_DATE_REQUIRED
            config.address = config.ADDRESS_SHOW

        context['config'] = config

        context['event'] = self.event
        context['info'] = self.info
        context['period'] = self.period
        context['lots'] = self.get_public_lots()
        context['available_lots'] = self.get_public_lots()
        context['has_available_lots'] = self.has_available_lots()
        context['has_paid_lots'] = self.has_paid_lots()

        context['paid_lots'] = self.get_all_lots()
        context['private_lots'] = self.get_private_lots()
        context['is_private_event'] = self.is_private_event()
        context['subscription_enabled'] = self.subscription_enabled()
        context['subscription_finished'] = self.subscription_finished()

        context['has_coupon'] = self.has_coupon()
        context['has_configured_bank_account'] = self.bank_account_configured
        context['has_active_bank_account'] = \
            self.active_bank_account_configured
        context['google_maps_api_key'] = settings.GOOGLE_MAPS_API_KEY

        return context

    def get_lots_queryset(self):
        return self.event.lots.order_by('date_end', 'name', 'price')

    def get_public_lots(self):
        if self.public_lots:
            return self.public_lots

        queryset = self.get_lots_queryset().filter(private=False, active=True)
        self.public_lots = [
            lot
            for lot in queryset
            if self.is_lot_running(lot)
        ]
        return self.public_lots

    def get_private_lots(self):
        if self.private_lots:
            return self.private_lots

        queryset = self.get_lots_queryset().filter(private=True, active=True)
        self.private_lots = [
            lot
            for lot in queryset
            if self.is_lot_running(lot)
        ]
        return self.private_lots

    def get_all_lots(self):
        return self.get_public_lots() + self.get_private_lots()

    def get_paid_lots(self):
        paid_lots = []
        for lot in self.get_all_lots():
            if lot.price and lot.price > 0:
                paid_lots.append(lot)

        return paid_lots

    def get_lot_status(self, lot):
        if lot.pk not in self.lot_statuses:
            self.lot_statuses[lot.pk] = lot.status

        return self.lot_statuses[lot.pk]

    def is_lot_running(self, lot):
        status = self.get_lot_status(lot)
        return status == lot.LOT_STATUS_RUNNING

    def has_available_lots(self):
        lots = self.get_all_lots()
        return lots and len(lots) > 0

    def has_available_private_lots(self):
        lots = self.get_private_lots()
        return lots and len(lots) > 0

    def has_available_public_lots(self):
        lots = self.get_public_lots()
        return lots and len(lots) > 0

    def has_paid_lots(self):
        """ Retorna se evento possui algum lote pago. """
        lots = self.get_paid_lots()
        return lots and len(lots) > 0

    def has_coupon(self):
        """ Retorna se possui cupom, seja qual for. """
        for lot in self.get_private_lots():
            # código de exibição
            if lot.private and lot.exhibition_code:
                return True

        return False

    def subscription_enabled(self):
        if self.has_available_lots() is False:
            return False

        return self.event.status == Event.EVENT_STATUS_NOT_STARTED

    def subscription_finished(self):
        for lot in self.get_all_lots():
            if self.is_lot_running(lot):
                return False

        return True

    def is_private_event(self):
        """ Verifica se evento é privado possuindo apenas lotes privados. """
        public_lots = self.get_public_lots()
        private_lots = self.get_private_lots()
        return len(public_lots) == 0 and len(private_lots) > 0


class SubscriptionFormMixin(EventMixin):
    form_class = PersonForm
    initial = {}
    object = None
    person = None
    subscription = None
    subscription_lot = None
    subscription_lot_available = False
    payments = None

    def get_person(self):
        """ Se usuario possui person """

        if self.person:
            return self.person

        if hasattr(self.request.user, 'person'):
            self.person = self.request.user.person
            return self.person

        return None

    def get_subscription(self):
        if self.subscription:
            return self.subscription

        try:
            self.subscription = Subscription.objects.get(
                person=self.get_person(),
                event=self.event,
                completed=True,
                test_subscription=False
            )

        except Subscription.DoesNotExist:
            pass

        return self.subscription

    def get_payments(self):
        if self.payments:
            return self.payments

        subscription = self.get_subscription()
        if not subscription:
            return None

        self.payments = subscription.transactions.filter(
            status=Transaction.PAID
        )

    def has_payments(self):
        payments = self.get_payments()
        return payments and len(self.get_payments()) > 0

    def get_subscription_lot(self):
        if self.subscription_lot:
            return self.subscription_lot

        sub = self.get_subscription()
        if not sub:
            return None

        try:
            self.subscription_lot = sub.lot
        except AttributeError:
            pass

        return self.subscription_lot

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_config'] = self.form_config

        if 'form' not in kwargs:
            context['form'] = self.get_form()

        person = self.get_person()
        sub = self.get_subscription()
        sub_lot = self.get_subscription_lot()

        context['person'] = person

        if person:
            context['subscription'] = sub
            context['is_subscribed'] = sub is not None
            context['lot_still_available'] = \
                sub_lot and self.is_lot_running(sub_lot)
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

        person = self.get_person()
        if 'instance' not in kwargs and person:
            kwargs['instance'] = person

        if self.request.method in ('POST', 'PUT'):
            if 'data' not in kwargs:
                kwargs.update({'data': self.request.POST})

        return kwargs

    def get_form(self, **kwargs):
        return self.form_class(**self.get_form_kwargs(**kwargs))


class SelectLotMixin(SubscriptionFormMixin):
    selected_lot = None
    exhibition_code = None

    def get_selected_lot(self):
        if self.selected_lot:
            return self.selected_lot

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
            sub_lot = self.get_subscription_lot()

            if sub_lot:
                self.selected_lot = sub_lot

        self.request.session['lot_pk'] = self.selected_lot.pk
        return self.selected_lot
