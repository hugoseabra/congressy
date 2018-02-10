from uuid import uuid4

import absoluteuri
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import HttpResponseNotAllowed, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import six
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views import generic
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters

from gatheros_event.forms import PersonForm
from gatheros_event.models import Event, Info, Member, Organization
from gatheros_subscription.models import Subscription, FormConfig, Lot
from mailer.services import (
    notify_new_user,
    notify_new_subscription,
)
from payment.exception import TransactionError
from payment.helpers import PagarmeTransactionInstanceData
from payment.models import Transaction
from payment.tasks import create_pagarme_transaction


class EventMixin(generic.View):
    event = None

    def dispatch(self, request, *args, **kwargs):
        self.event = get_object_or_404(Event, slug=self.kwargs.get('slug'))
        response = super().dispatch(request, *args, **kwargs)
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['event'] = self.event
        context['info'] = get_object_or_404(Info, event=self.event)
        context['period'] = self.get_period()
        context['lots'] = self.get_lots()
        context['subscription_enabled'] = self.subscription_enabled()
        context['has_paid_lots'] = self.has_paid_lots()
        context[
            'has_configured_bank_account'] = \
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

    def subscription_enabled(self):
        if self.event.subscription_type == Event.SUBSCRIPTION_DISABLED:
            return False

        lots = self.get_lots()
        if len(lots) == 0:
            return False

        return self.event.status == Event.EVENT_STATUS_NOT_STARTED

    def get_period(self):
        """ Resgata o prazo de duração do evento. """
        return self.event.get_period()

    def get_lots(self):
        lots = self.event.lots.all()
        return [lot for lot in lots if lot.status == lot.LOT_STATUS_RUNNING]


class SubscriptionFormMixin(EventMixin, generic.FormView):
    form_class = PersonForm
    initial = {}
    object = None
    person = None

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

        context['person'] = self.get_person()
        context['is_subscribed'] = self.is_subscribed()

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

    def is_subscribed(self):
        """
            Se já estiver inscrito retornar True
        """
        user = self.request.user

        if user.is_authenticated:
            try:
                person = user.person
                Subscription.objects.get(person=person, event=self.event)
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


class HotsiteView(SubscriptionFormMixin, generic.View):
    template_name = 'hotsite/main.html'

    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    def post(self, request, *args, **kwargs):

        user = self.request.user

        if user.is_authenticated:
            email = user.email
            name = user.person.name

        else:
            name = self.request.POST.get('name')
            email = self.request.POST.get('email')

        if not self.subscription_enabled():
            return HttpResponseNotAllowed([])

        if user.is_authenticated:
            return redirect(
                'public:hotsite-subscription',
                slug=self.event.slug
            )

        context = self.get_context_data(**kwargs)
        context['remove_preloader'] = False

        if not name or not email:
            messages.error(
                self.request,
                "Você deve informar todos os dados para fazer a sua inscrição."
            )

            context['name'] = name
            context['email'] = email

            return self.render_to_response(context)

        if user.is_anonymous and self.subscriber_has_account(email):
            messages.info(
                self.request,
                'Faça login para continuar sua inscrição.'
            )

            login_url = '{}?next={}'.format(
                reverse('public:login'),
                reverse('public:hotsite', kwargs={
                    'slug': self.event.slug
                })
            )

            return redirect(login_url)

        with transaction.atomic():
            # Criando usuário
            password = str(uuid4())
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password
            )

            self.initial = {
                'email': email,
                'name': name
            }

            form = self.get_form()
            form.setAsRequired('email')

            if not form.is_valid():
                context['form'] = form
                return self.render_to_response(context)

            person = form.save()
            person.user = user
            person.save()

            self._configure_brand_person(person)
            self._notify_new_account(user)

            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)

            # Remove last login para funcionar o reset da senha posteriormente.
            user.last_login = None
            user.save()

        return redirect('public:hotsite-subscription', slug=self.event.slug)

    def _configure_brand_person(self, person):
        """ Configura nova pessoa cadastrada. """

        # Criando organização interna
        with transaction.atomic():
            try:
                person.members.get(organization__internal=True)
            except Member.DoesNotExist:
                internal_org = Organization(
                    internal=True,
                    name=person.name
                )

                for attr, value in six.iteritems(person.get_profile_data()):
                    setattr(internal_org, attr, value)

                internal_org.save()

                Member.objects.create(
                    organization=internal_org,
                    person=person,
                    group=Member.ADMIN
                )

    def _notify_new_account(self, user):

        url = absoluteuri.reverse(
            'password_reset_confirm',
            kwargs={
                'uidb64': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user)
            }
        )

        context = {
            'email': user.email,
            'url': url,
            'site_name': get_current_site(self.request)
        }

        notify_new_user(context)


class HotsiteSubscriptionView(SubscriptionFormMixin, generic.View):
    template_name = 'hotsite/subscription.html'
    form_class = PersonForm

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)

        if not request.user.is_authenticated:
            return redirect('public:hotsite', slug=self.event.slug)

        subscribed = self.is_subscribed()
        enabled = self.subscription_enabled()
        if not enabled:
            return redirect('public:hotsite', slug=self.event.slug)

        return response

    def get_form(self, **kwargs):
        form = super().get_form(**kwargs)

        try:
            config = self.event.formconfig
        except AttributeError:
            config = FormConfig()
            config.event = self.event

        required_fields = ['gender']

        has_paid_lots = self.has_paid_lots()

        if has_paid_lots or config.phone:
            required_fields.append('phone')

        if has_paid_lots or config.address_show:
            required_fields.append('street')
            required_fields.append('village')
            required_fields.append('zip_code')
            required_fields.append('city')

        if not has_paid_lots and not config.address_show:
            required_fields.append('city')

        if has_paid_lots or config.cpf_required:
            required_fields.append('cpf')

        if has_paid_lots or config.birth_date_required:
            required_fields.append('birth_date')

        for field_name in required_fields:
            form.setAsRequired(field_name)

        return form

    def get_context_data(self, **kwargs):
        cxt = super().get_context_data(**kwargs)

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

        cxt['config'] = config
        cxt['remove_preloader'] = True
        cxt['pagarme_encryption_key'] = settings.PAGARME_ENCRYPTION_KEY

        return cxt

    def post(self, request, *args, **kwargs):

        request.POST = request.POST.copy()

        user = self.request.user

        if not user.is_authenticated or not self.subscription_enabled():
            return HttpResponseNotAllowed([])

        def clear_string(field_name):
            if field_name not in request.POST:
                return

            value = request.POST.get(field_name)
            value = value.replace('.', '').replace('-', '').replace('/', '')

            request.POST[field_name] = value

        clear_string('cpf')
        clear_string('zip_code')

        context = self.get_context_data(**kwargs)
        context['remove_preloader'] = True

        allowed_transaction = request.POST.get('allowed_transaction', False)

        if allowed_transaction:
            request.session['allowed_transaction'] = allowed_transaction
            slug = kwargs.get('slug')
            return HttpResponseRedirect(
                reverse('public:hotsite-subscription', args={slug}))

        with transaction.atomic():
            form = self.get_form()
            if form.initial and not form.is_valid():
                slug = kwargs.get('slug')
                return HttpResponseRedirect(
                    reverse('public:hotsite-subscription', args={slug}))

            if not form.is_valid():
                context['form'] = form
                return self.render_to_response(context)

            if self.has_paid_lots() and 'transaction_type' not in request.POST:
                messages.error(
                    request=self.request,
                    message='Por favor escolha um tipo de pagamento.'
                )
                return self.render_to_response(context)

            person = form.save()

            if self.has_paid_lots():
                lot_pk = self.request.POST.get('lot')
            else:
                lot_pk = self.event.lots.first().pk

            # Garante que o lote é do evento
            lot = get_object_or_404(Lot, event=self.event, pk=lot_pk)
            #
            try:
                subscription = Subscription.objects.get(lot=lot, person=person,
                                                        event=self.event)
                subscription.event = self.event
                subscription.person = person
                subscription.created_by = user.id
            except Subscription.DoesNotExist:
                subscription = Subscription(
                    person=person,
                    lot=lot,
                    created_by=user.id
                )

            subscription.save()

            if self.has_paid_lots():
                try:
                    transaction_instance_data = PagarmeTransactionInstanceData(
                        person=person,
                        extra_data=request.POST,
                        event=self.event
                    )

                    create_pagarme_transaction(
                        payment=transaction_instance_data.transaction_instance_data,
                        subscription=subscription
                    )

                except TransactionError as e:
                    error_dict = {
                        'No transaction type': 'Por favor escolher uma forma de pagamento.',
                        'Transaction type not allowed': 'Forma de pagamento não permitida.',
                        'Organization has no bank account': 'Organização não está podendo receber pagamentos no momento.',
                        'No organization': 'Evento não possui organizador.',
                    }
                    if e.message in error_dict:
                        e.message = error_dict[e.message]
                    messages.error(self.request, message=e.message)
                    return self.render_to_response(context)

            subscription.save()
            notify_new_subscription(self.event, subscription)

            messages.success(
                self.request,
                'Inscrição realizada com sucesso!'
            )

        if self.has_paid_lots():
            return redirect(
                'public:hotsite-subscription-status',
                slug=self.event.slug
            )

        return redirect('public:hotsite', slug=self.event.slug)


class HotsiteSubscriptionStatusView(EventMixin, generic.TemplateView):
    template_name = 'hotsite/subscription_status.html'
    person = None
    subscription = None

    def dispatch(self, request, *args, **kwargs):

        response = super().dispatch(request, *args, **kwargs)

        self.person = self.get_person()

        if not request.user.is_authenticated or not self.person:
            return redirect('public:hotsite', slug=self.event.slug)

        self.is_subscribed()

        if not self.subscription:
            messages.error(message='Você não possui inscrição neste evento.',
                           request=request)
            return redirect('public:hotsite', slug=self.event.slug)

        return response

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context['person'] = self.get_person()
        context['is_subscribed'] = self.is_subscribed()
        context['transactions'] = self.get_transactions()
        context['allow_transaction'] = self.get_allowed_transaction()
        context['pagarme_key'] = settings.PAGARME_ENCRYPTION_KEY

        try:
            context['subscription'] = self.subscription.pk
        except AttributeError:
            context['subscription'] = Subscription.objects.get(
                event=self.event, person=self.person)

        context['subscription'] = self.subscription

        return context

    def get_person(self):
        """ Se usuario possui person """
        if not self.request.user.is_authenticated or self.person:
            return self.person
        else:
            try:
                self.person = self.request.user.person
            except (ObjectDoesNotExist, AttributeError):
                pass

        return self.person

    def is_subscribed(self):
        """
            Se já estiver inscrito retornar True
        """
        user = self.request.user

        if user.is_authenticated:
            try:
                person = user.person
                subscription = Subscription.objects.get(person=person,
                                                        event=self.event)
                self.subscription = subscription
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

    def get_transactions(self):

        try:
            transactions = Transaction.objects.filter(
                subscription=self.subscription)
        except Transaction.DoesNotExist:
            return False

        return transactions

    def get_allowed_transaction(self):

        found_boleto = False
        found_credit_card = False

        try:
            transactions = Transaction.objects.filter(
                subscription=self.subscription)

            for transaction in transactions:
                if transaction.data['payment_method'] == 'boleto':
                    found_boleto = True
                elif transaction.data['payment_method'] == 'credit_card':
                    found_credit_card = True
                if found_boleto and found_credit_card:
                    return False
        except Transaction.DoesNotExist:
            return False

        if found_credit_card:
            return 'boleto'

        if found_boleto:
            return 'credit_card'

        return True
