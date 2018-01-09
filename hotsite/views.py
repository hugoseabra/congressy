from datetime import datetime
from uuid import uuid4

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.views.generic import DetailView
from django.urls import reverse
from django.contrib import messages
from django.utils import six
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail

from django.core.exceptions import ValidationError
from gatheros_event.models import Event, Info, Person, Member, Organization
from gatheros_subscription.models import Lot, Subscription


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
        return context

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

        email = self.request.POST.get('email')
        name = self.request.POST.get('name')
        phone = self.request.POST.get('phone')
        user = self.request.user

        self.object = self.get_object()

        shiny_user = None
        full_reset_url = ''

        if not email or not name or not phone:

            if not email:
                messages.error(self.request, "E-mail não pode estar vazio!")

            if not name:
                messages.error(self.request, "Nome não pode estar vazio!")

            if not phone:
                messages.error(self.request, "Phone não pode estar vazio!")

            context = super(HotsiteView, self).get_context_data(**kwargs)
            context['status'] = self._get_status()
            context['report'] = self._get_report()
            context['period'] = self._get_period()
            context['name'] = name
            context['email'] = email
            context['info'] = Info.objects.get(pk=self.object.pk)
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
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            domain = 'http://localhost:8000'
            full_reset_url = domain + '/reset-password/confirmation/' + str(
                uid, 'utf-8') + "/" + str(token)

            # Criando organização interna
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

        lot = Lot.objects.get(event=self.object)
        subscription = Subscription(
            person=person,
            lot=lot,
            created_by=user.id
        )

        try:
            subscription.save()
            # Send an email here

            email_subject = "Congressy: Sucesso! Você está cadastrado no" \
                            " evento: {0}".format(self.object.name)

            if shiny_user:
                email_template = """

    Olá {2},

        Seja bem-vindo a Congressy Plataforma de Eventos!

        Sucesso! Foi feito o seu cadastro no evento: {0}
    
        Click no link abaixo para confirmar seu email:
    
        {1}
    
    Equipe Congressy,
                """.format(self.object.name, full_reset_url, name)
            else:
                email_template = """

    Olá {1},
    
        Sucesso! Foi feito o seu cadastro no evento: {0}
        
    Equipe Congressy,
                """.format(self.object.name, name)

            send_mail(email_subject, email_template, ['equipe@congressy.com'],
                      [email])

            messages.success(self.request, 'Inscrição realizada com sucesso!')

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
        return render(
            self.request,
            template_name=self.template_name,
            context=context
        )
