from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import HttpResponseNotAllowed, Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import six
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters

from core.views.mixins import TemplateNameableMixin
from gatheros_event.forms import PersonForm
from gatheros_event.models import Event, Info, Member, Organization
from gatheros_subscription.models import FormConfig, Lot, Subscription
from mailer.services import (
    notify_new_free_subscription,
    notify_new_user_and_free_subscription,
)
from payment.exception import TransactionError
from payment.helpers import PagarmeTransactionInstanceData
from payment.models import Transaction
from payment.tasks import create_pagarme_transaction


class EventMixin(TemplateNameableMixin, generic.View):
    event = None

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug')

        if not slug:
            return redirect('https://congressy.com')

        self.event = get_object_or_404(Event, slug=self.kwargs.get('slug'))
        response = super().dispatch(request, *args, **kwargs)
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['event'] = self.event
        context['info'] = get_object_or_404(Info, event=self.event)
        context['period'] = self.get_period()
        context['lots'] = self.get_lots()
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

        lots = self.get_lots()
        if len(lots) == 0:
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
        return self.event.lots.filter(private=False)

    def get_private_lots(self):
        return self.event.lots.filter(private=True)


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


class HotsiteView(SubscriptionFormMixin, generic.View):
    template_name = 'hotsite/main.html'

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
        if not self.subscription_enabled():
            return HttpResponseNotAllowed([])

        context = self.get_context_data(**kwargs)
        context['remove_preloader'] = False

        name = self.request.POST.get('name')
        email = self.request.POST.get('email')

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
            return redirect(
                'public:hotsite-subscription',
                slug=self.event.slug
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
                    'slug': self.event.slug
                })
            )

            return redirect(login_url)

        # Condição 5
        elif has_account:

            is_subscribed = self.is_subscribed(email=email)

            if is_subscribed:
                context['remove_preloader'] = True
                context['is_subscribed_and_never_logged_in'] = True
                context['email'] = email
                return self.render_to_response(context)

            # Override anonymous user
            user = User.objects.get(email=email)

            try:
                person = user.person
            except AttributeError:
                # Garante que usuário sempre terá pessoa.
                form = get_person_form(user)
                if not form.is_valid():
                    context['form'] = form
                    return self.render_to_response(context)
                person = form.save()

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

        return redirect('public:hotsite-subscription', slug=self.event.slug)

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


class HotsiteSubscriptionView(SubscriptionFormMixin, generic.View):
    template_name = 'hotsite/subscription.html'
    form_class = PersonForm

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)

        if not request.user.is_authenticated:
            return redirect('public:hotsite', slug=self.event.slug)

        enabled = self.subscription_enabled()
        if not enabled:
            return redirect('public:hotsite', slug=self.event.slug)

        # Se o já inscrito e porém, não há lotes pagos, não há o que
        # fazer aqui.
        if self.is_subscribed() and self.has_paid_lots():
            return redirect(
                'public:hotsite-subscription-status',
                slug=self.event.slug
            )

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
        """
        CONDIÇÃO 1: usuário não autenticado ou inscrições não disponíveis
            - retorna a página inicial

        CONDIÇÃO 2: dados inválidos
            - retorna a página de inscrição com devidas mensagens de erro(s)

        CONDIÇÃO 3: verificação de conta (nova ou usuáro ativo [já logou])
            - seta uma 'flag' da verficação para futuras condicionais

        CONDIÇÃO 4: usuário já inscrito
            - seta uma 'flag' da verficação para futuras condicionais

        CONDIÇÃO 5: inscrição gratuita
            - se inscrição não existe, cria inscrição
            - se inscrição já existe, edit inscrição
            - notifica usuário;
            - redireciona para página inicial;

        CONDIÇÃO 6: lote pago, ação proibido
            - verificação: não há lotes pagos e transação não permitida
            - redireciona usuário para página de inscrição com mensagem e erro

        CONDIÇÃO 7: lote pago, transação permitida
            - se inscrição não existe, cria inscrição
            - se inscrição já existe, edit inscrição
            - processa pagamento;
            - notifica usuário;
            - redireciona para página de status

        CONDIÇÂO 8: status da inscrição
            - verifica o tipo de lotes, caso não tenha lotes pagos, então a inscrição é confirmada
        """
        context = self.get_context_data(**kwargs)
        context['remove_preloader'] = True

        user = self.request.user

        # CONDIÇÃO 7
        # if self.has_paid_lots():
        #     allowed_transaction = request.POST.get(
        #         'allowed_transaction',
        #         False
        #     )
        #
        #     # CONDIÇÃO 6
        #     if allowed_transaction:
        #         request.session['allowed_transaction'] = allowed_transaction
        #         slug = kwargs.get('slug')
        #         return redirect('public:hotsite-subscription', slug=slug)

        # CONDIÇÃO 1
        if not user.is_authenticated or not self.subscription_enabled():
            return HttpResponseNotAllowed([])

        # CONDIÇÃO 2
        request.POST = request.POST.copy()

        def clear_string(field_name):
            if field_name not in request.POST:
                return

            value = request.POST.get(field_name)

            if not value:
                return ''

            value = value \
                .replace('.', '') \
                .replace('-', '') \
                .replace('/', '') \
                .replace('(', '') \
                .replace(')', '') \
                .replace(' ', '')

            request.POST[field_name] = value

        clear_string('cpf')
        clear_string('zip_code')
        clear_string('phone')
        clear_string('institution_cnpj')

        form = self.get_form()

        if not form.is_valid():
            context['slug'] = kwargs.get('slug')
            context['form'] = form
            return self.render_to_response(context)

        person = form.save()

        # CONDIÇÃO 3
        new_account = user.last_login is None

        # CONDIÇÃO 4
        new_subscription = False

        try:
            subscription = Subscription.objects.get(
                person=person,
                event=self.event
            )
        except Subscription.DoesNotExist:
            subscription = Subscription(
                person=person,
                event=self.event,
                created_by=user.id
            )
            new_subscription = True

        # Resgata e verifica lote se houver
        if 'lot' in request.POST:
            lot_pk = self.request.POST.get('lot')

            # Garante que o lote é do evento
            try:
                lot = self.event.lots.get(pk=lot_pk)
            except Lot.DoesNotExist:
                messages.error(
                    self.request,
                    "Este lote não pertence a este evento."
                )
                return self.render_to_response(context)

        else:
            # Inscrição simples
            lot = self.event.lots.first()

        # Insere ou edita lote
        subscription.lot = lot

        if self.has_paid_lots():
            # CONDIÇÃO 7
            if 'transaction_type' not in request.POST:
                messages.error(
                    request=self.request,
                    message='Por favor escolha um tipo de pagamento.'
                )
                return self.render_to_response(context)

            try:
                with transaction.atomic():

                    subscription.save()

                    transaction_data = PagarmeTransactionInstanceData(
                        subscription=subscription,
                        extra_data=request.POST.copy(),
                        event=self.event
                    )

                    create_pagarme_transaction(
                        transaction_data=transaction_data,
                        subscription=subscription
                    )

            except TransactionError as e:
                error_dict = {
                    'No transaction type': \
                        'Por favor escolher uma forma de pagamento.',
                    'Transaction type not allowed': \
                        'Forma de pagamento não permitida.',
                    'Organization has no bank account': \
                        'Organização não está podendo receber pagamentos no'
                        ' momento.',
                    'No organization': 'Evento não possui organizador.',
                }
                if e.message in error_dict:
                    e.message = error_dict[e.message]

                messages.error(self.request, message=e.message)
                return self.render_to_response(context)

        else:
            # CONDIÇÃO 8
            subscription.status = subscription.CONFIRMED_STATUS
            subscription.save()

            # CONDIÇÃO 5 e 7
            if new_account and new_subscription:
                notify_new_user_and_free_subscription(self.event, subscription)

            else:
                notify_new_free_subscription(self.event, subscription)

        messages.success(
            self.request,
            'Inscrição realizada com sucesso!'
        )

        if self.has_paid_lots():
            # CONDIÇÃO 7
            return redirect(
                'public:hotsite-subscription-status',
                slug=self.event.slug
            )

        # CONDIÇÃO 5
        return redirect('public:hotsite', slug=self.event.slug)


class HotsiteSubscriptionStatusView(EventMixin, generic.TemplateView):
    template_name = 'hotsite/subscription_status.html'
    person = None
    subscription = None

    def dispatch(self, request, *args, **kwargs):

        response = super().dispatch(request, *args, **kwargs)

        self.person = self.get_person()

        # Se  não há lotes pagos, não há o que fazer aqui.
        if not self.has_paid_lots():
            return redirect(
                'public:hotsite',
                slug=self.event.slug
            )

        try:
            self.subscription = Subscription.objects.get(
                event=self.event, person=self.person)

            if not request.user.is_authenticated or not self.person:
                return redirect('public:hotsite', slug=self.event.slug)

            return response

        except Subscription.DoesNotExist:
            messages.error(
                message='Você não possui inscrição neste evento.',
                request=request
            )
            return redirect('public:hotsite', slug=self.event.slug)

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context['person'] = self.get_person()
        context['is_subscribed'] = self.is_subscribed()
        context['transactions'] = self.get_transactions()
        context['allow_transaction'] = self.get_allowed_transaction()
        context['pagarme_key'] = settings.PAGARME_ENCRYPTION_KEY
        context['remove_preloader'] = True
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


class CouponView(EventMixin, generic.TemplateView):
    template_name = 'hotsite/includes/form_lots_coupon.html'
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):

        cxt = self.get_context_data(**kwargs)

        code = request.POST.get('coupon')
        if code:
            try:
                lot = Lot.objects.get(exhibition_code=str(code).upper())

                if lot.status != Lot.LOT_STATUS_RUNNING:
                    raise Http404

                cxt['lot'] = lot
                return self.render_to_response(cxt)

            except Lot.DoesNotExist:
                pass

        raise Http404
