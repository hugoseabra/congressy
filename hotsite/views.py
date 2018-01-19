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
from gatheros_subscription.models import Subscription
from mailer.services import (
    notify_new_user,
)


class EventMixin(generic.View):
    event = None

    def dispatch(self, request, *args, **kwargs):
        self.event = get_object_or_404(Event, slug=self.kwargs.get('slug'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['event'] = self.event
        context['info'] = get_object_or_404(Info, event=self.event)
        context['period'] = self._get_period()
        context['lots'] = self._get_lots()

        return context

    def _get_period(self):
        """ Resgata o prazo de duração do evento. """
        return self.event.get_period()

    def _get_lots(self):
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

        if not 'instance' in kwargs and self.person:
            kwargs['instance'] = self.person

        if self.request.method in ('POST', 'PUT'):
            if not 'data' in kwargs:
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

        context['person'] = self._get_person()
        context['is_subscribed'] = self._is_subscribed()

        return context

    def _get_person(self):
        """ Se usuario possui person """

        if self.person or not self.request.user.is_authenticated:
            return self.person

        try:
            self.person = self.request.user.person
        except (ObjectDoesNotExist, AttributeError):
            pass

        return self.person

    def _is_subscribed(self):
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

    def _subscriber_has_account(self, email):
        if self.request.user.is_authenticated:
            return True

        try:
            user = User.objects.get(email=email)
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

        lot = self.request.POST.get('lot')

        if self.event.subscription_type == Event.SUBSCRIPTION_DISABLED:
            return HttpResponseNotAllowed()

        context = self.get_context_data(**kwargs)
        context['remove_preloader'] = True

        if not name or not email or not lot:
            messages.error(
                self.request,
                "Você deve informar todos os dados para fazer a sua inscrição."
            )

            context['name'] = name
            context['email'] = email

            return self.render_to_response(context)

        if user.is_anonymous and self._subscriber_has_account(email):
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

        #Criando organização interna
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


        # if self.person is None:
        #     # hard post
        # 
        #     # gender = self.request.POST.get('gender')
        # 
        #     # Criando perfil
        #     person = Person(name=name, email=email, phone=phone)
        # 
        #     # Criando usuário
        #     password = str(uuid4())
        #     user = User.objects.create_user(
        #         username=email,
        #         email=email,
        #         password=password
        #     )
        # 
        #     # Vinculando usuário ao perfil
        #     person.user = user
        #     person.save()
        # 
        #     # Criando a senha par o email de confirmação e definição de
        #     # senha
        #     """
        #     Generates a one-use only link for resetting password and sends to the
        #     user.
        #     """
        #     shiny_user = True
        #     full_reset_url = absoluteuri.reverse(
        #         'password_reset_confirm',
        #         kwargs={
        #             'uidb64': urlsafe_base64_encode(force_bytes(user.pk)),
        #             'token': default_token_generator.make_token(user)
        #         }
        #     )
        # 
        #     # Criando organização interna
        #     try:
        #         person.members.get(organization__internal=True)
        #     except Member.DoesNotExist:
        #         internal_org = Organization(
        #             internal=True,
        #             name=person.name
        #         )
        # 
        #         for attr, value in six.iteritems(
        #                 person.get_profile_data()):
        #             setattr(internal_org, attr, value)
        # 
        #         internal_org.save()
        # 
        #         Member.objects.create(
        #             organization=internal_org,
        #             person=person,
        #             group=Member.ADMIN
        #         )
        # 
        # lot = Lot.objects.get(event=self.object)
        # subscription = Subscription(
        #     person=person,
        #     lot=lot,
        #     created_by=user.id
        # )
        # 
        # try:
        # 
        #     subscription.save()
        # 
        #     if shiny_user:
        #         notify_new_user_and_subscription(
        #             self.object,
        #             subscription,
        #             full_reset_url
        #         )
        #     else:
        #         notify_new_subscription(self.object, subscription)
        # 
        #     messages.success(self.request,
        #                      'Inscrição realizada com sucesso!')
        # 
        # except ValidationError as e:
        #     error_message = e.messages[0]
        #     if error_message:
        #         messages.error(self.request, error_message)
        #     else:
        #         messages.error(self.request,
        #                        'Ocorreu um erro durante a o processo de inscrição, tente novamente mais tarde.')

    # context = super(HotsiteView, self).get_context_data(**kwargs)
    # context['status'] = self._get_status()
    # context['report'] = self._get_report()
    # context['period'] = self._get_period()
    # context['name'] = name
    # context['email'] = email
    # context['info'] = Info.objects.get(pk=self.object.pk)
    # context['is_subscribed'] = self._get_subscribed_status()
    # context['remove_preloader'] = True
    # return render_to_response(
    #     self.request,
    #     template_name=self.template_name,
    #     context=context
    # )



    # def get_form(self):
    #
    #     if not form:
    #         form = self.form_class(**self.get_form_kwargs())
    #
    #     try:
    #         config = self.object.formconfig
    #
    #         required_fields = ['gender']
    #
    #         if config.phone:
    #             required_fields.append('phone')
    #
    #         if not config.address_show and config.city:
    #             required_fields.append('city')
    #         else:
    #             required_fields.append('street')
    #             required_fields.append('village')
    #             required_fields.append('zip_code')
    #             required_fields.append('city')
    #
    #         if config.cpf_required:
    #             required_fields.append('cpf')
    #
    #         if config.birth_date_required:
    #             required_fields.append('birth_date')
    #
    #         for field_name in required_fields:
    #             form.setAsRequired(field_name)
    #
    #     except AttributeError:
    #         pass
    #
    #     return form



class HotsiteSubscriptionView(SubscriptionFormMixin, generic.View):
    template_name = 'hotsite/subscription.html'

    # NÃO AUTENTICADO, VAZA