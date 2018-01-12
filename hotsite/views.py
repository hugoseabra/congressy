from datetime import datetime
from uuid import uuid4

import absoluteuri
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import six
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views.generic import DetailView

from gatheros_event.models import Event, Info, Person, Member, Organization
from gatheros_subscription.models import Lot, Subscription
from mailer.services import (
    notify_new_user_and_subscription,
    notify_new_subscription,
)


class HotsiteView(DetailView):
    model = Event
    template_name = 'hotsite/base.html'
    object = None

    # form_template = 'hotsite/form.html'

    def get_context_data(self, **kwargs):
        context = super(HotsiteView, self).get_context_data(**kwargs)
        context['status'] = self._get_status()
        context['report'] = self._get_report()
        context['period'] = self._get_period()
        context['info'] = Info.objects.get(pk=self.object.pk)
        context['person'] = self._get_person()
        context['is_subscribed'] = self._get_subscribed_status()
        return context

    def _get_person(self):
        """
            Se usuario possuir person
        """
        user = self.request.user

        if user.is_authenticated:
            try:
                person = Person.objects.get(email=user.email)
                if person:
                    return person
            except ObjectDoesNotExist:
                pass

        return False

    def _get_subscribed_status(self):
        """
            Se já estiver inscrito retornar True
        """
        user = self.request.user

        if user.is_authenticated:
            try:
                person = Person.objects.get(email=user.email)
                found = Subscription.objects.filter(person_id=person.pk,
                                                    event_id=self.object.id)
                if found:
                    return True
            except ObjectDoesNotExist:
                pass

        return False

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

    def _get_period(self):
        """ Resgata o prazo de duração do evento. """
        return self.object.get_period()

    def post(self, request, *args, **kwargs):

        self.object = self.get_object()

        user = self.request.user
        email = self.request.POST.get('email')
        name = self.request.POST.get('name')
        phone = self.request.POST.get('phone')

        if self.object.data['subscription_type'] != Event.SUBSCRIPTION_DISABLED:

            shiny_user = None
            full_reset_url = ''

            if not email or not name or not phone:

                if not email:
                    messages.error(self.request,
                                   "E-mail não pode estar vazio!")

                if not name:
                    messages.error(self.request, "Nome não pode estar vazio!")

                if not phone:
                    messages.error(self.request,
                                   "Celluar não pode estar vazio!")

                context = super(HotsiteView, self).get_context_data(**kwargs)
                context['status'] = self._get_status()
                context['report'] = self._get_report()
                context['period'] = self._get_period()
                context['name'] = name
                context['email'] = email
                context['info'] = Info.objects.get(pk=self.object.pk)
                context['remove_preloader'] = True
                return render(self.request, template_name=self.template_name,
                              context=context)

            try:
                user = User.objects.get(email=email)
                logged_in = self.request.user.is_authenticated

                if user != self.request.user and not logged_in and user.last_login:
                    messages.error(self.request, 'Faça login para continuar.')

                    full_url = '{}?next={}'.format(
                        reverse('public:login'),
                        reverse('public:hotsite', kwargs={
                            'slug': self.object.slug
                        })
                    )

                    return HttpResponseRedirect(full_url)

            except User.DoesNotExist:
                pass

            try:
                person = Person.objects.get(email=email)

                if phone:
                    person.phone = phone
                    person.save()

            except Person.DoesNotExist:

                # hard post

                # gender = self.request.POST.get('gender')

                # Criando perfil
                person = Person(name=name, email=email, phone=phone)

                # Criando usuário
                password = str(uuid4())
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=password
                )

                # Vinculando usuário ao perfil
                person.user = user
                person.save()

                # Criando a senha par o email de confirmação e definição de senha
                """
                Generates a one-use only link for resetting password and sends to the
                user.
                """
                shiny_user = True
                url = '/reset-password/confirmation/{uid}/{token}/'.format(
                    uid=urlsafe_base64_encode(force_bytes(user.pk)),
                    token=default_token_generator.make_token(user)
                )

                full_reset_url = absoluteuri.build_absolute_uri(url)

                # Criando organização interna
                try:
                    person.members.get(organization__internal=True)
                except Member.DoesNotExist:
                    internal_org = Organization(
                        internal=True,
                        name=person.name
                    )

                    for attr, value in six.iteritems(
                            person.get_profile_data()):
                        setattr(internal_org, attr, value)

                    internal_org.save()

                    Member.objects.create(
                        organization=internal_org,
                        person=person,
                        group=Member.ADMIN
                    )

            lot = Lot.objects.get(event=self.object)
            subscription = Subscription(
                person=person,
                lot=lot,
                created_by=user.id
            )

            try:

                subscription.save()

                if shiny_user:
                    notify_new_user_and_subscription(
                        self.object,
                        subscription,
                        full_reset_url
                    )
                else:
                    notify_new_subscription(self.object, subscription)

                messages.success(self.request,
                                 'Inscrição realizada com sucesso!')

            except ValidationError as e:
                error_message = e.messages[0]
                if error_message:
                    messages.error(self.request, error_message)
                else:
                    messages.error(self.request,
                                   'Ocorreu um erro durante a o processo de inscrição, tente novamente mais tarde.')

        context = super(HotsiteView, self).get_context_data(**kwargs)
        context['status'] = self._get_status()
        context['report'] = self._get_report()
        context['period'] = self._get_period()
        context['name'] = name
        context['email'] = email
        context['info'] = Info.objects.get(pk=self.object.pk)
        context['is_subscribed'] = self._get_subscribed_status()
        context['remove_preloader'] = True
        return render(
            self.request,
            template_name=self.template_name,
            context=context
        )
