from datetime import datetime

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import HttpResponseNotAllowed
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import six
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters

from gatheros_event.helpers.publishing import event_is_publishable, \
    get_unpublishable_reason
from gatheros_event.models import Member, Organization
from gatheros_subscription.models import Subscription
from hotsite.views import SubscriptionFormMixin


class HotsiteView(SubscriptionFormMixin, generic.FormView):
    template_name = 'hotsite/main.html'
    has_private_subscription = False
    private_still_available = False

    def dispatch(self, request, *args, **kwargs):
        self.pre_dispatch()

        is_anonymous = self.request.user.is_anonymous
        is_in_org = False
        person = None

        if not is_anonymous:
            person = self.request.user.person

        if person:
            org_pk = self.current_event.event.organization_id
            try:
                Member.objects.get(organization_id=org_pk, person_id=person.pk)
                is_in_org = True
            except Member.DoesNotExist:
                pass

        if is_anonymous or not is_in_org:
            if not self.current_event.event.published:
                return redirect("public:unpublished-hotsite")

        if 'has_private_subscription' in self.request.session:

            subscription_id = self.request.session['has_private_subscription']

            try:
                Subscription.objects.get(
                    pk=subscription_id,
                    lot__private=True,
                    event__slug=self.kwargs.get('slug')
                )
                self.has_private_subscription = True
            except Subscription.DoesNotExist:
                pass

        response = super().dispatch(request, *args, **kwargs)

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        sub = self.current_subscription.subscription
        event = self.current_event.event

        # Força verificação se está inscrito apenas para inscrições completas.
        context['is_subscribed'] = sub.completed is True if sub else False

        context['has_private_subscription'] = self.has_private_subscription
        context['private_still_available'] = self.has_private_subscription

        publishable = False
        unpublishable_reason = None

        if not event.published:
            publishable = event_is_publishable(event)
            unpublishable_reason = get_unpublishable_reason(event)

        context['event_is_publishable'] = publishable
        context['unpublishable_reason'] = unpublishable_reason

        return context

    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    def post(self, request, *args, **kwargs):
        """
        CONDIÇÃO 0 - Inscrições não disponíveis:
            - redireciona para página inical.

        CONDIÇÃO 1 - Usuário logado:
            - redireciona para página de formulário de inscrição.

        CONDIÇÃO 2 - Nome e/ou e-mail não informado:
            - retorna a página com mensagem de erro

        CONDIÇÃO 3 - Sobrenome não informado:
            - retorna a página com mensagem de erro

        CONDIÇÃO 4 - Usuário não logado, possui conta e já logou:
            - Caso já tenha logado, pedir para entrar com suas credenciais;

        CONDIÇÃO 5 - Usuário não logado, possui conta e nunca logou:
            - Caso nunca tenha logado, o sistema deve se comportar como um
              usuário novo;
            - Caso usuario já tenha logado,redireciona para página de inscrição;
            - Caso usuario tenha conta, nunca logou e já está inscrito,
            redirectiona para definir senha.

        CONDIÇÃO 6 - Usuário não logado, não possui conta:
            - Cria pesssoa;
            - Se dados válidos, cria pessoa;
            - Se dados não válidos, retorna para formulário com mensagem de
              erro;
            - Cria configurar pessoa (organização interna);
            - Cria usuário;
            - redireciona para página de inscrição;
        """
        # CONDIÇÃO 0
        if not self.current_event.event.published:
            return HttpResponseNotAllowed([])

        context = self.get_context_data(**kwargs)
        context['remove_preloader'] = False

        name = self.request.POST.get('name')
        email = self.request.POST.get('email')
        exihibition_code = None

        is_private_event = self.current_event.is_private_event()

        if is_private_event:
            exihibition_code = self.request.POST.get('exhibition_code')

        # Pode acontecer caso que há usuário e não há pessoa.
        def get_person_form(user=None):
            self.initial = {
                'email': email,
                'name': name
            }

            form = self.get_form()
            form.setAsRequired('email')

            if form.is_valid():
                person = form.save()

                if not user:
                    # Criando usuário
                    user = User.objects.create_user(
                        username=email,
                        email=email
                    )

                person.user = user
                person.save()

                self._configure_brand_person(person)

            return form

        # CONDIÇÃO 1
        user = self.request.user

        if user.is_authenticated:

            if is_private_event and not exihibition_code:
                messages.error(
                    self.request,
                    "Você deve informar um código válido para se inscrever"
                    " neste evento."
                )
                if 'exhibition_code' in request.session:
                    del request.session['exhibition_code']

                context['exhibition_code'] = exihibition_code
                return self.render_to_response(context)

            # Registra código para verificação mais adiante
            request.session['exhibition_code'] = exihibition_code

            return redirect(
                'public:hotsite-subscription',
                slug=self.current_event.slug
            )

        # CONDIÇÃO 2
        if not name or not email:
            messages.error(
                self.request,
                "Você deve informar todos os dados para fazer a sua inscrição."
            )

            context['name'] = name
            context['email'] = email
            return self.render_to_response(context)

        if is_private_event and not exihibition_code:
            messages.error(
                self.request,
                "Você deve informar um código válido para se inscrever neste"
                " evento."
            )

            context['exhibition_code'] = exihibition_code
            return self.render_to_response(context)

        # CONDIÇÃO 3
        email = email.lower()

        try:
            split_name = name.strip().split(' ')
            # array clean
            split_name = list(filter(None, split_name))

            if not split_name or len(split_name) == 1:
                raise Exception()

            first = split_name[0].strip()
            surnames = [n.strip() for n in split_name[1:]]

            name = '{} {}'.format(first, ' '.join(surnames))

        except Exception:
            messages.error(
                self.request,
                "Você deve informar seu sobrenome para fazer a sua inscrição."
            )

            context['name'] = name
            context['email'] = email
            return self.render_to_response(context)

        # CONDIÇÃO 4
        has_account = self.subscriber_has_account(email)
        has_logged = self.subscriber_has_logged(email)

        if has_account and has_logged:
            messages.info(
                self.request,
                'Faça login para continuar sua inscrição.'
            )

            login_url = '{}?next={}'.format(
                reverse('public:login'),
                reverse('public:hotsite', kwargs={
                    'slug': self.current_event.slug
                })
            )

            return redirect(login_url)

        # Condição 5
        elif has_account:

            is_subscribed = \
                self.current_subscription.subscription.is_new is False

            if is_subscribed:
                context['remove_preloader'] = True
                context['is_subscribed_and_never_logged_in'] = True
                context['email'] = email
                return self.render_to_response(context)

            # Override anonymous user
            user = User.objects.get(email=email)

            if not hasattr(user, 'person') and user.person:
                # Garante que usuário sempre terá pessoa.
                form = get_person_form(user)

                if not form.is_valid():
                    context['form'] = form
                    return self.render_to_response(context)

                form.save()

        # Condição 6
        else:
            # Nova pessoa.
            form = get_person_form()
            if not form.is_valid():
                context['form'] = form
                return self.render_to_response(context)

            person = form.save()
            user = person.user

        # Inscrição realizada com participante autenticado.
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)

        if not has_logged:
            # Remove last login para funcionar o reset da senha posteriormente.
            user.last_login = None
            user.save()

        if is_private_event:
            # Registra código para verificação mais adiante
            request.session['exhibition_code'] = exihibition_code

        return redirect(
            'public:hotsite-subscription',
            slug=self.current_event.slug
        )

    def _configure_brand_person(self, person):
        """ Configura nova pessoa cadastrada. """

        if not person.members.count():
            org = Organization(internal=False, name=person.name)

            for attr, value in six.iteritems(person.get_profile_data()):
                setattr(org, attr, value)

            org.save()

            Member.objects.create(
                organization=org,
                person=person,
                group=Member.ADMIN
            )

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
        if self.request.user.is_authenticated:
            return True

        try:
            user = User.objects.get(email=email)
            return user.last_login is not None
        except User.DoesNotExist:
            pass

        return False

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
                    completed=True,
                    test_subscription=False,
                    event=self.current_event.event
                )
                return True
            except (Subscription.DoesNotExist, AttributeError):
                pass

        return False

class UnpublishHotsiteView(generic.TemplateView):
    template_name = 'hotsite/unpublished.html'
