from uuid import uuid4

import absoluteuri
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import six
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views import generic

from gatheros_event.forms import PersonForm
from gatheros_event.models import Event, Info, Member, Organization
from gatheros_subscription.models import Subscription, FormConfig, Lot
from mailer.services import (
    notify_new_user,
    notify_new_subscription,
)
from payment.tasks import create_credit_card_transaction, create_boleto_transaction


class EventMixin(generic.View):
    event = None

    def dispatch(self, request, *args, **kwargs):
        self.event = get_object_or_404(Event, slug=self.kwargs.get('slug'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['event'] = self.event
        context['info'] = get_object_or_404(Info, event=self.event)
        context['period'] = self.get_period()
        context['lots'] = self.get_lots()
        context['subscription_enabled'] = self.subscription_enabled()
        context['has_paid_lots'] = self.has_paid_lots()

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
    template_name = 'hotsite/base.html'

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
        context['remove_preloader'] = True

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
            self._notify_new_account(person)

            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)

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

    def _notify_new_account(self, person):

        user = person.user

        url = absoluteuri.reverse(
            'password_reset_confirm',
            kwargs={
                'uidb64': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user)
            }
        )

        context = {
            'email': person.email,
            'url': url,
            'site_name': get_current_site(self.request)
        }

        notify_new_user(context)


class HotsiteSubscriptionView(SubscriptionFormMixin, generic.View):
    template_name = 'hotsite/subscription.html'

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)

        if not request.user.is_authenticated:
            return redirect('public:hotsite', slug=self.event.slug)

        subscribed = self.is_subscribed()
        enabled = self.subscription_enabled()
        if not enabled or subscribed:
            return redirect('public:hotsite', slug=self.event.slug)

        return response

    def get_form(self, **kwargs):
        form = super().get_form(**kwargs)

        try:
            config = self.event.formconfig
        except AttributeError:
            config = FormConfig()

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

        with transaction.atomic():
            form = self.get_form()

            if not form.is_valid():
                context['form'] = form
                return self.render_to_response(context)

            if request.POST['payment_type'] == 'credit_card' and not request.POST['card_hash']:
                context['form'] = form
                return self.render_to_response(context)

            person = form.save()

            if self.has_paid_lots():
                lot_pk = self.request.POST.get('lot')
            else:
                lot_pk = self.event.lots.first().pk

            # Garante que o lote é do evento
            lot = get_object_or_404(Lot, event=self.event, pk=lot_pk)

            subscription = Subscription(
                person=person,
                lot=lot,
                created_by=user.id
            )

            if request.POST['payment_type'] == 'credit_card':
                transaction_instance_data = {
                    "price": int(lot.price * 100),
                    "card_hash": request.POST['card_hash'],
                    "customer": {
                        "name": form.cleaned_data['name'],
                        "type": "individual",
                        "country": "br",
                        "email": form.cleaned_data['email'],
                        "documents": [
                            {
                                "type": "cpf",
                                "number": form.cleaned_data['cpf'],
                            }
                        ],
                        "phone_numbers": [
                            "+55" + form.cleaned_data['phone'].replace(" ", "").replace('(', '').replace(')',
                                                                                                         '').replace(
                                '-', '')],
                        "birthday": form.cleaned_data['birth_date'].strftime('%Y-%d-%m'),
                    },
                    "billing": {
                        "name": form.cleaned_data['name'],
                        "address": {
                            "country": "br",
                            "state": form.cleaned_data['city'].uf.lower(),
                            "city": form.cleaned_data['city'].name.lower().capitalize(),
                            "neighborhood": form.cleaned_data['village'],
                            "street": form.cleaned_data['street'],
                            "street_number": form.cleaned_data['number'],
                            "zipcode": form.cleaned_data['zip_code']
                        }
                    },
                    "event_name": context['event'].organization.name,
                    'recipient_id': context['event'].organization.recipient_id,
                }
                create_credit_card_transaction(transaction_instance_data)
            elif request.POST['payment_type'] == 'boleto':
                transaction_instance_data = {

                    "price": int(lot.price * 100),

                    "customer": {
                        "name": form.cleaned_data['name'],
                        "type": "individual",
                        "country": "br",
                        "email": form.cleaned_data['email'],
                        "documents": [
                            {
                                "type": "cpf",
                                "number": form.cleaned_data['cpf'],
                            }
                        ],
                        "phone_numbers": [
                            "+55" + form.cleaned_data['phone'].replace(" ", "").replace('(', '').replace(')',
                                                                                                         '').replace(
                                '-', '')],
                        "birthday": form.cleaned_data['birth_date'].strftime('%Y-%d-%m'),
                    },

                    "billing": {
                        "name": form.cleaned_data['name'],
                        "address": {
                            "country": "br",
                            "state": form.cleaned_data['city'].uf.lower(),
                            "city": form.cleaned_data['city'].name.lower().capitalize(),
                            "neighborhood": form.cleaned_data['village'],
                            "street": form.cleaned_data['street'],
                            "street_number": form.cleaned_data['number'],
                            "zipcode": form.cleaned_data['zip_code']
                        }
                    },

                    "event_name": context['event'].organization.name,

                    'recipient_id': context['event'].organization.recipient_id,
                }


                create_boleto_transaction(transaction_instance_data)

            subscription.save()
            notify_new_subscription(self.event, subscription)

            messages.success(
                self.request,
                'Inscrição realizada com sucesso!'
            )

        return redirect('public:hotsite-subscription', slug=self.event.slug)
