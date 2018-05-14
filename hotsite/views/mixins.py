"""
    Mixins usados no módulo de hotsite.
"""

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, redirect
from django.views import generic

from core.views.mixins import TemplateNameableMixin
from gatheros_event.forms import PersonForm
from gatheros_event.models import Event, Info
from gatheros_subscription.models import FormConfig, Lot, \
    Subscription


class EventMixin(TemplateNameableMixin, generic.View):
    event = None

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug')

        if not slug:
            return redirect('https://congressy.com')

        self.event = get_object_or_404(Event, slug=slug)
        response = super().dispatch(request, *args, **kwargs)
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            config = self.event.formconfig
        except AttributeError:
            config = FormConfig()

        if self.has_paid_lots():
            config.email = True
            config.phone = True
            config.city = True

            config.cpf = config.CPF_REQUIRED
            config.birth_date = config.BIRTH_DATE_REQUIRED
            config.address = config.ADDRESS_SHOW

        context['config'] = config

        context['event'] = self.event
        context['info'] = get_object_or_404(Info, event=self.event)
        context['period'] = self.get_period()
        context['lots'] = self.get_available_lots()
        context['paid_lots'] = [
            lot
            for lot in self.get_lots()
            if lot.status == lot.LOT_STATUS_RUNNING
        ]
        context['private_lots'] = [
            lot
            for lot in self.get_private_lots()
            if lot.status == lot.LOT_STATUS_RUNNING
        ]
        context['subscription_enabled'] = self.subscription_enabled()
        context['subsciption_finished'] = self.subsciption_finished()
        context['has_paid_lots'] = self.has_paid_lots()
        context['has_available_lots'] = self.has_available_lots()
        context['available_lots'] = self.get_available_lots()
        context['has_coupon'] = self.has_coupon()
        context['has_configured_bank_account'] = \
            self.event.organization.is_bank_account_configured()
        context['has_active_bank_account'] = \
            self.event.organization.active_recipient
        context['google_maps_api_key'] = settings.GOOGLE_MAPS_API_KEY

        return context

    def has_paid_lots(self):
        """ Retorna se evento possui algum lote pago. """
        for lot in self.event.lots.all():
            price = lot.price
            if price is None:
                continue

            if lot.price > 0:
                return True

        return False

    def has_coupon(self):
        """ Retorna se possui cupon, seja qual for. """
        for lot in self.event.lots.all():
            # código de exibição
            if lot.private and lot.exhibition_code:
                return True

        return False

    def subscription_enabled(self):

        if self.has_available_lots() is False:
            return False

        return self.event.status == Event.EVENT_STATUS_NOT_STARTED

    def subsciption_finished(self):
        for lot in self.event.lots.all():
            if lot.status == Lot.LOT_STATUS_RUNNING:
                return False

        return True

    def get_period(self):
        """ Resgata o prazo de duração do evento. """
        return self.event.get_period()

    def get_lots(self):
        return [
            lot
            for lot in self.event.lots.filter(private=False )
            if lot.status == lot.LOT_STATUS_RUNNING
        ]

    def get_private_lots(self):
        return [
            lot
            for lot in self.event.lots.filter(private=True)
            if lot.status == lot.LOT_STATUS_RUNNING
        ]

    def has_available_lots(self):
        available_lots = []

        for lot in self.event.lots.all():
            if lot.status == lot.LOT_STATUS_RUNNING:
                available_lots.append(lot)

        return True if len(available_lots) > 0 else False

    def has_available_public_lots(self):
        available_lots = []

        all_events = self.event.lots.filter(private=False)

        for lot in all_events:
            if lot.status == lot.LOT_STATUS_RUNNING:
                available_lots.append(lot)

        return True if len(available_lots) > 0 else False

    def get_available_lots(self):
        all_lots = self.event.lots.filter(private=False)
        available_lots = []

        for lot in all_lots:
            if lot.status == lot.LOT_STATUS_RUNNING:
                available_lots.append(lot)

        return available_lots


class SubscriptionFormMixin(EventMixin, generic.FormView):
    form_class = PersonForm
    initial = {}
    object = None
    person = None
    subscription = None

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if 'form' not in kwargs:
            context['form'] = self.get_form()

        try:
            context['form_config'] = self.object.formconfig
        except (ObjectDoesNotExist, AttributeError):
            pass

        person = self.get_person()

        if person:
            try:
                context['subscription'] = \
                    Subscription.objects.get(person=person,
                                             event=self.event)
                context['is_subscribed'] = True
            except Subscription.DoesNotExist:
                context['is_subscribed'] = False

        else:
            context['is_subscribed'] = False

        context['person'] = person

        return context

    def get_person(self):
        """ Se usuario possui person """

        if self.person or not self.request.user.is_authenticated:
            return self.person

        try:
            self.person = self.request.user.person
        except (ObjectDoesNotExist, AttributeError):
            pass

        return self.person

    def is_subscribed(self, email=None):
        """
            Se já estiver inscrito retornar True
        """
        if email:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return False
        else:
            user = self.request.user

        if user.is_authenticated:
            try:
                person = user.person
                Subscription.objects.get(
                    person=person,
                    event=self.event
                )
                return True
            except (Subscription.DoesNotExist, AttributeError):
                pass

        return False

    def subscriber_has_account(self, email):
        if self.request.user.is_authenticated:
            return True

        try:
            User.objects.get(email=email)
            return True

        except User.DoesNotExist:
            pass

        return False

    def subscriber_has_logged(self, email):
        try:
            user = User.objects.get(email=email)
            return user.last_login is not None

        except User.DoesNotExist:
            pass

        return False
