from datetime import datetime
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.transaction import atomic
from django.forms import ValidationError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import ugettext as _
from formtools.wizard.forms import ManagementForm
from formtools.wizard.views import SessionWizardView

from core.helpers import sentry_log
from core.util.string import clear_string
from gatheros_event.helpers.event_business import is_paid_event
from gatheros_subscription.models import Subscription
from hotsite import forms
from hotsite.views.mixins import SelectLotMixin
from mailer.services import (
    notify_new_free_subscription,
    notify_new_user_and_free_subscription,
)
from payment.exception import TransactionError
from payment.helpers.payment_helpers import (
    get_opened_boleto_transactions,
    is_boleto_allowed,
)
from payment.models import Transaction

FORMS = [
    ("service", forms.ServiceForm),
    ("product", forms.ProductForm),
    ("person", forms.SubscriptionPersonForm),
    ("payment", forms.PaymentForm)
]

TEMPLATES = {
    "service": "hotsite/service_form.html",
    "product": "hotsite/product_form.html",
    "person": "hotsite/person_form.html",
    "payment": "hotsite/payment_form.html"
}


class InvalidStateStepError(Exception):
    """ Exceção acontece quando um step de formulário não possui
     um estado esperado. """
    pass


def has_pending_payment(wizard):
    subscription = wizard.subscription

    ##########################################################################
    # Verifica se já existe pagamentos aguardando serem processados.
    ##########################################################################
    for transaction in subscription.transactions.all():
        is_cc = transaction.type == Transaction.CREDIT_CARD
        is_boleto = transaction.type == Transaction.BOLETO
        boleto_expiration_date = transaction.boleto_expiration_date
        today = datetime.date(datetime.now())
        if transaction.status == Transaction.WAITING_PAYMENT:

            if is_boleto:
                if boleto_expiration_date \
                        and boleto_expiration_date < today:
                    return False
                else:
                    return True

            if is_cc:
                return True

        # NO caso de cartão de crédito, pode haver um delay no processamento
        if transaction.status == Transaction.PROCESSING and is_cc:
            return True

    return False


def can_process_payment(wizard):
    """ Verifica se pagamento pode ser processado no wizard. """
    if wizard.storage.current_step == "payment":
        return True

    subscription = wizard.subscription

    ev_has_paid_products = has_paid_products(wizard)
    ev_has_paid_services = has_paid_services(wizard)

    if ev_has_paid_services is False and ev_has_paid_products is False:
        # Para eventos gratuitos que não possuem atividades extras ou
        # opcionais pagos, não processar pagamento.
        return False

    # Verificando se inscrição possui vínculo com alguma das atividades
    # extras e/ou opcionais.
    num_paid_products = subscription.subscription_products.filter(
        optional_price__gt=0
    ).count()
    num_paid_services = subscription.subscription_services.filter(
        optional_price__gt=0
    ).count()

    if num_paid_products == 0 and num_paid_services == 0:
        # Se a inscrição não possui vinculo com atividades  extras e
        # opcionais pagos.
        return False

    # Se o lote selecionado é pago, independente das atividades extras e/ou
    # opcionais, o pagamento poderá ser processado.

    if has_pending_payment(wizard):
        # Porém, se inscrição já possui pagamento pendente.
        return False

    # Tudo certo, vamos processar o pagamento.
    return True


def _has_services(lot):
    try:
        optionals = lot.category.service_optionals
        return optionals.filter(
            published=True,
            date_end_sub__gte=datetime.now(),
        ).count() > 0 and lot.event.feature_configuration.feature_services

    except AttributeError:
        return False


def _has_products(lot):
    try:
        optionals = lot.category.product_optionals
        return optionals.filter(
            published=True,
            date_end_sub__gte=datetime.now(),
        ).count() > 0

    except AttributeError:
        return False


def has_products(wizard):
    lot = wizard.subscription.lot

    return _has_products(lot)


def has_services(wizard):
    lot = wizard.subscription.lot

    return _has_services(lot)


def has_paid_products(wizard):
    lot = wizard.subscription.lot

    try:
        optionals = lot.category.product_optionals
        for optional in optionals.all():
            if optional.price and optional.price > 0 and \
                    lot.event.feature_configuration.feature_products:
                return True

    except AttributeError:
        return False

    return False


def has_paid_services(wizard):
    lot = wizard.subscription.lot

    try:
        optionals = lot.category.service_optionals
        for optional in optionals.all():
            if optional.price and optional.price > 0 and \
                    lot.event.feature_configuration.feature_services:
                return True

    except AttributeError:
        return False

    return False


class OptionalWizardView(SessionWizardView, SelectLotMixin):
    condition_dict = {
        'payment': can_process_payment,
        'service': has_services,
        'product': has_products,
    }

    def __init__(self, **kwargs):
        self.event = None
        self.subscription = None
        self.person = None
        self.top_bar = False
        self.loaded_forms = {}
        super().__init__(**kwargs)

    def pre_dispatch(self):
        super().pre_dispatch()

        self.event = self.current_event.event
        self.subscription = self.current_subscription.subscription

        if 'conversion_unique_id' not in self.request.session:
            # Ponto de controle para saber que participante passou pelo
            # wizard e leva informação para o /subscription/done/
            self.request.session['conversion_unique_id'] = \
                str(self.subscription.pk)

    def dispatch(self, request, *args, **kwargs):
        path = request.path
        self.top_bar = '/subscription/' in path

        self.pre_dispatch()

        user = self.request.user
        if not isinstance(user, User):
            return redirect('public:hotsite', slug=self.event.slug)

        if not self.current_event.subscription_enabled():
            return redirect('public:hotsite', slug=self.event.slug)

        lot = self.current_subscription.lot

        if not _has_services(lot) and not _has_products(lot):
            messages.warning(
                request,
                "Seu lote não possui atividades extras e/ou opcionais "
                "disponíveis no momento."
            )
            return redirect('public:hotsite', slug=self.event.slug)

        try:
            if self.current_subscription.has_payments():
                messages.warning(
                    request,
                    "Você já possui uma inscrição paga neste evento."
                )

            if self.event.is_scientific and hasattr(self.event, 'work_config'):
                if not self.event.work_config.is_configured:
                    return redirect('public:hotsite', slug=self.event.slug)

            return super().dispatch(request, *args, **kwargs)

        except InvalidStateStepError as e:

            sentry_log(str(e), type='error', notify_admins=True)

            messages.warning(
                request,
                "Por favor, informe os dados do início para validarmos"
                " as informações de sua inscrição."
            )

            return redirect(
                'public:hotsite-subscription',
                slug=self.event.slug
            )

    def post(self, *args, **kwargs):
        """
        This method handles POST requests.

        The wizard will render either the current step (if form validation
        wasn't successful), the next step (if the current step was stored
        successful) or the done view (if no more steps are available)
        """
        # Look for a wizard_goto_step element in the posted data which
        # contains a valid step name. If one was found, render the requested
        # form. (This makes stepping back a lot easier).

        wizard_goto_step = self.request.POST.get('wizard_goto_step', None)
        if wizard_goto_step and wizard_goto_step in self.get_form_list():
            return self.render_goto_step(wizard_goto_step)

        # Check if form was refreshed
        management_form = ManagementForm(self.request.POST, prefix=self.prefix)
        if not management_form.is_valid():
            raise ValidationError(
                _('ManagementForm data is missing or has been tampered.'),
                code='missing_management_form',
            )

        form_current_step = management_form.cleaned_data['current_step']
        if (form_current_step != self.steps.current and
                self.storage.current_step is not None):
            # form refreshed, change current step
            self.storage.current_step = form_current_step

        # @TODO: Fix this ugly hack for pre-form cleaning
        # Copy is needed, QueryDict is immutable
        post_data = self.request.POST.copy()
        post_data = self.clear_string('person-institution_cnpj',
                                      data=post_data)
        post_data = self.clear_string('person-cpf', data=post_data)
        post_data = self.clear_string('person-zip_code', data=post_data)
        post_data = self.clear_string('person-phone', data=post_data)

        # get the form for the current step
        # @TODO: Fix this ugly hack for pre-form cleaning
        # This should be receiving self.request.POST no post_data
        form = self.get_form(data=post_data, files=self.request.FILES)

        # and try to validate
        while form.is_valid():
            # if the form is valid, store the cleaned data and files.
            try:
                self.storage.set_step_data(self.steps.current,
                                           self.process_step(form))
                # self.storage.set_step_files(self.steps.current,
                #                             self.process_step_files(form))
            except ValidationError as e:

                if hasattr(e, 'message'):
                    form.add_error('__all__', e.message)
                elif hasattr(e, 'error_dict'):
                    for field, err in e:
                        form.add_error(field, err)
                elif hasattr(e, 'error_list'):
                    for err in e:
                        form.add_error('__all__', err)
                else:
                    raise Exception('Unknown ValidationError message.')
                break

            # check if the current step is the last step
            if self.steps.current == self.steps.last:
                # no more steps, render done view
                return self.render_done(form, **kwargs)
            else:
                # proceed to the next step
                return self.render_next_step(form, **kwargs)

        return self.render(form)

    def get_form(self, step=None, data=None, files=None):
        if step is None:
            step = self.steps.current

        if step in self.loaded_forms and data is None:
            form = self.loaded_forms[step]
            if form.data is None:
                return self.loaded_forms[step]

        form = super().get_form(step, data, files)
        self.loaded_forms[step] = form
        return form

    def get_form_kwargs(self, step=None):
        kwargs = super().get_form_kwargs(step)

        if step == "private_lot":
            kwargs.update({
                'event': self.event,
                'code': self.request.session.get('exhibition_code'),
                'excluded_lot_pk': None,
            })

        if step == 'lot':
            kwargs.update({
                'event': self.event,
                'excluded_lot_pk': None,
            })

        if step == 'person':
            kwargs.update({
                'user': self.request.user,
                'lot': self.get_lot(),
                'event': self.event,
            })

        if step == 'survey':
            lot = self.get_lot()

            kwargs.update({
                'subscription': self.current_subscription.subscription,
                'lot': lot,
                'event_survey': lot.event_survey,
            })

        if step == 'payment':
            kwargs.update({
                'selected_lot': self.get_lot(),
                'subscription': self.current_subscription.subscription,
            })

        return kwargs

    def process_step(self, form):

        if not form.is_valid():
            raise ValidationError(form.errors)

        form_data = self.get_form_step_data(form)
        # form_files = self.get_form_step_files(form)

        # Persisting person
        if isinstance(form, forms.SubscriptionPersonForm):
            # Resgata lote apenas para saber se ele está na session
            self.get_lot()

            if not form.is_valid():
                raise ValidationError(form.errors)

            self.person = form.save()

        # Persisting payments:
        if isinstance(form, forms.PaymentForm):
            # Resgata lote apenas para saber se ele está na session
            self.get_lot()

            if not form.is_valid():
                raise ValidationError(form.errors)

            try:
                form.save()

            # except DebtAlreadyPaid as e:
            #     raise ValidationError(str(e))

            except TransactionError as e:
                raise ValidationError(str(e))

        return form_data

    # noinspection PyUnresolvedReferences
    def get_next_step(self, step=None):
        """
        Returns the next step after the given `step`. If no more steps are
        available, None will be returned. If the `step` argument is None, the
        current step will be determined automatically.
        """
        if step is None:
            step = self.steps.current
        form_list = self.get_form_list()
        keys = list(form_list.keys())

        # This is a hack, to return to the first step, when we get a ValueError
        # See: https://intra.congressy.com/congressy/congressy/issues/2453/
        try:
            key = keys.index(step) + 1
        except ValueError:
            return keys[0]

        if len(keys) > key:
            return keys[key]
        return None

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context['remove_preloader'] = True

        context['num_lots'] = len(self.current_event.get_all_lots())
        context['subscription'] = self.subscription
        context['is_last'] = self.steps.current == self.steps.last
        context['has_top_bar'] = self.top_bar

        person = self.subscription.person
        context['person'] = person

        lot = self.subscription.lot
        context['selected_lot'] = lot

        opened_boletos = self.get_open_boleto()
        has_open_boleto = \
            opened_boletos.count() > 0 if opened_boletos else False

        context['has_open_boleto'] = has_open_boleto

        if self.storage.current_step == 'person':

            config = self.current_event.form_config

            if is_paid_event(self.current_event.event):
                config.email = True
                config.phone = True
                config.city = True

                config.cpf = config.CPF_REQUIRED
                config.birth_date = config.BIRTH_DATE_REQUIRED
                config.address = config.ADDRESS_SHOW

            context['config'] = config

        if self.storage.current_step == 'payment':
            context['pagarme_encryption_key'] = settings.PAGARME_ENCRYPTION_KEY
            context['lot'] = self.get_lot()

            allowed_types = [Transaction.CREDIT_CARD]
            is_brazilian = person.country == 'BR'

            if is_boleto_allowed(self.event) \
                    and has_open_boleto is False \
                    and is_brazilian is True:
                allowed_types.append(Transaction.BOLETO)

            context['allowed_transaction_types'] = ','.join(allowed_types)

            subscription = self.subscription
            context['subscription'] = subscription

            total = subscription.lot.get_calculated_price() or Decimal(0.00)

            products = [x for x in subscription.subscription_products.all()]
            context['products'] = products

            services = [x for x in subscription.subscription_services.all()]
            context['services'] = services

            for product in products:
                total += product.optional_price

            for service in services:
                total += service.optional_price

            context['total'] = total

        return context

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def done(self, form_list, **kwargs):

        subscription = self.subscription
        subscription.lot = self.get_lot()

        with atomic():
            try:
                subscription.completed = True
                subscription.save()
                transactions_qs = self.subscription.transactions

                paid_products = subscription.subscription_products.filter(
                    optional_price__gt=0
                ).count() > 0
                paid_services = subscription.subscription_services.filter(
                    optional_price__gt=0
                ).count() > 0

                has_paid_optionals = paid_products or paid_services
                is_free = has_paid_optionals is False and subscription.free

                new_account = self.request.user.last_login is None

                if is_free:
                    subscription.status = Subscription.CONFIRMED_STATUS
                    subscription.save()

                    has_transactions = transactions_qs.count() > 0

                    if has_transactions is True:
                        paid_transaction = transactions_qs.filter(
                            status=Transaction.PAID
                        ).count() > 0

                        if paid_transaction is True:
                            msg_trans = 'Você já possui pagamento de' \
                                        ' de outro lote.'
                            messages.warning(self.request, msg_trans)

                        msg_trans = 'Por favor, ignore os boletos que ainda' \
                                    ' não estejam vencidos.'

                        messages.warning(self.request, msg_trans)

                    if subscription.notified is False:
                        if new_account is True:
                            notify_new_user_and_free_subscription(
                                self.event,
                                subscription
                            )

                        else:
                            notify_new_free_subscription(
                                self.event,
                                subscription
                            )

                        msg = 'Inscrição realizada com sucesso!' \
                              ' Nós lhe enviamos um e-mail de confirmação de' \
                              ' sua inscrição juntamente com seu voucher.' \
                              ' Fique atento ao seu email, e, caso não' \
                              ' chegue na caixa de entrada, verifique no' \
                              ' Lixo Eletrônico.'

                        subscription.notified = True
                        subscription.save()

                    else:
                        msg = 'Inscrição salva com sucesso!'

                else:
                    has_transactions = transactions_qs.exclude(
                        subscription__lot=subscription.lot
                    ).count() > 0

                    if has_transactions is True:
                        paid_transaction = transactions_qs.filter(
                            status=Transaction.PAID
                        ).exclude(
                            subscription__lot=subscription.lot
                        ).count() > 0

                        if paid_transaction is True:
                            msg_trans = 'Você já possui pagamento de' \
                                        ' de outro lote.'
                            messages.warning(self.request, msg_trans)

                        msg_trans = 'Por favor, ignore os boletos que ainda' \
                                    ' não estejam vencidos.'

                        messages.warning(self.request, msg_trans)

                    if subscription.notified is False:
                        msg = 'Inscrição realizada com sucesso! Nós lhe' \
                              ' enviamos um e-mail de confirmação de sua' \
                              ' inscrição. Após a confirmação de seu' \
                              ' pagamento, você receberá outro email com' \
                              ' seu voucher. Fique atento ao seu email, e,' \
                              ' caso não chegue na caixa de entrada,' \
                              ' verifique no Lixo Eletrônico.'
                    else:
                        msg = 'Inscrição salva com sucesso!'

                success_url = reverse_lazy(
                    'public:hotsite-subscription-done',
                    kwargs={'slug': self.event.slug, }
                )

                messages.success(self.request, msg)
                return redirect(success_url)

            except Exception as e:

                raise InvalidStateStepError('Algum erro ocorreu: {}'.format(e))

    def get_lot(self):
        selected_lot = self.get_selected_lot()

        if not selected_lot:
            raise InvalidStateStepError(
                'Nenhum lote selecionado foi encontrado.')

        return selected_lot

    def get_open_boleto(self):
        return get_opened_boleto_transactions(self.subscription)

    # noinspection PyMethodMayBeStatic
    def clear_string(self, field_name, data):
        if data and field_name in data:
            value = data.get(field_name)
            if value:
                data[field_name] = clear_string(value)
        return data
