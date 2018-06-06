from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.transaction import atomic
from django.forms import ValidationError
from django.http import QueryDict, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.translation import ugettext as _
from formtools.wizard.forms import ManagementForm
from formtools.wizard.views import SessionWizardView

from gatheros_event.models import Event, Person
from gatheros_subscription.models import FormConfig, Lot, Subscription
from hotsite import forms
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
from survey.directors import SurveyDirector

FORMS = [
    ("private_lot", forms.PrivateLotForm),
    ("lot", forms.LotsForm),
    ("person", forms.SubscriptionPersonForm),
    ("survey", forms.SurveyForm),
    ("service", forms.ServiceForm),
    ("product", forms.ProductForm),
    ("payment", forms.PaymentForm)
]

TEMPLATES = {
    "private_lot": "hotsite/private_lot_form.html",
    "lot": "hotsite/lot_form.html",
    "person": "hotsite/person_form.html",
    "survey": "hotsite/survey_form.html",
    "service": "hotsite/service_form.html",
    "product": "hotsite/product_form.html",
    "payment": "hotsite/payment_form.html"
}


class InvalidStateStepError(Exception):
    """ Exceção acontece quando um step de formulário não possui
     um estado esperado. """
    pass


def is_paid_lot(wizard):
    """Return true if user opts for  a paid lot"""

    # Get cleaned data from lots step
    cleaned_data = wizard.get_cleaned_data_for_step('private_lot')
    if not cleaned_data:
        cleaned_data = wizard.get_cleaned_data_for_step('lot') or {
            'lots': 'none'}

    # Return true if lot has price and price > 0
    if cleaned_data:
        lot = cleaned_data['lots']

        if isinstance(lot, Lot):
            if lot.price and lot.price > 0:
                return True

    return False


def can_process_payment(wizard):
    """ Verifica se pagamento pode ser processado no wizard. """
    subscription = wizard.get_subscription()

    if is_paid_lot(wizard) is False:
        return False

    has_boleto_waiting = False
    has_card_waiting = False
    for transaction in subscription.transactions.all():
        is_cc = transaction.type == Transaction.CREDIT_CARD
        is_boleto = transaction.type == Transaction.BOLETO
        if transaction.status == Transaction.WAITING_PAYMENT:
            if is_boleto:
                has_boleto_waiting = True

            if is_cc:
                has_card_waiting = True

        # NO caso de cartão de crédito, pode haver um delay no processamento
        if transaction.status == Transaction.PROCESSING and is_cc:
            has_card_waiting = True

    deny_payment = has_card_waiting is True and has_boleto_waiting is True

    return deny_payment is False


def has_survey(wizard):
    """ Return true if user opts for a lot with survey"""

    # Get cleaned data from lots step
    cleaned_data = wizard.get_cleaned_data_for_step('private_lot')
    if not cleaned_data:
        cleaned_data = wizard.get_cleaned_data_for_step('lot') or {
            'lots': 'none'}

    if cleaned_data:

        # Return true if lot has price and price > 0
        lot = cleaned_data['lots']

        if isinstance(lot, Lot):

            if lot.event_survey and lot.event_survey.survey.questions.count() > 0:
                return True

    return False


def is_private_event(wizard):
    return wizard.is_private_event()


def is_not_private_event(wizard):
    return not wizard.is_private_event()


def has_products(wizard):
    # Get cleaned data from lots step
    cleaned_data = wizard.get_cleaned_data_for_step('lot') or {'lots': 'none'}

    # Return true if lot has price and price > 0
    lot = cleaned_data['lots']

    if isinstance(lot, Lot) and lot.category:
        return lot.category.product_optionals.count() > 0

    return False


def has_services(wizard):
    # Get cleaned data from lots step
    if is_private_event(wizard):
        data = wizard.get_cleaned_data_for_step('private_lot') or {}
    else:
        data = wizard.get_cleaned_data_for_step('lot') or {}

    lot = data.get('lots')

    if lot and isinstance(lot, Lot) and lot.category:
        return lot.category.service_optionals.count() > 0

    return False


class SubscriptionWizardView(SessionWizardView):
    condition_dict = {
        'private_lot': is_private_event,
        'lot': is_not_private_event,
        'payment': can_process_payment,
        'survey': has_survey,
        'service': has_services,
        'product': has_products,
    }
    event = None
    person = None
    subscription = None

    def dispatch(self, request, *args, **kwargs):

        slug = self.kwargs.get('slug')

        if not slug:
            return redirect('https://congressy.com')

        self.event = get_object_or_404(Event, slug=slug)

        user = self.request.user
        if not isinstance(user, User):
            return redirect('public:hotsite', slug=self.event.slug)

        if not self.subscription_enabled():
            return redirect('public:hotsite', slug=self.event.slug)

        if self.has_paid_subscription():
            messages.warning(
                request,
                "Você já possui uma inscrição paga neste evento."
            )
            # return redirect(
            #     'public:hotsite-subscription-status',
            #     slug=self.event.slug
            # )

        if self.is_private_event() and not self.has_previous_valid_code():
            messages.error(
                request,
                "Você deve informar um código válido para se inscrever neste"
                " evento."
            )
            self.clear_session_exhibition_code()
            return redirect('public:hotsite', slug=self.event.slug)

        if self.event.is_scientific:
            if not self.event.work_config or not \
                    self.event.work_config.is_submittable:
                return redirect('public:hotsite', slug=self.event.slug)

        try:
            return super().dispatch(request, *args, **kwargs)
        except InvalidStateStepError as e:

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
                self.storage.set_step_files(self.steps.current,
                                            self.process_step_files(form))
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
                return self.render_next_step(form)

        return self.render(form)

    def get_form_kwargs(self, step=None):
        kwargs = super().get_form_kwargs(step)

        if step == "private_lot":
            kwargs.update({
                'event': self.event,
                'code': self.request.session.get('exhibition_code')
            })

        if step == 'lot':
            kwargs.update({'event': self.event, })

        if step == 'person':
            kwargs.update({
                'user': self.request.user,
                'lot': self.get_lot(),
                'event': self.event,
            })

        if step == 'survey':
            lot = self.get_lot()
            kwargs.update({
                'user': self.request.user,
                'event': self.event,
                'event_survey': lot.event_survey,
            })

        if step == 'payment':
            kwargs.update({
                'selected_lot': self.get_lot(),
                'subscription': self.get_subscription(),
            })

        return kwargs

    def process_step(self, form):

        if not form.is_valid():
            raise ValidationError(form.errors)

        form_data = self.get_form_step_data(form)

        # Creating a subscription.
        if isinstance(form, forms.LotsForm) or \
                isinstance(form, forms.PrivateLotForm):

            lot_pk = None
            if isinstance(form, forms.PrivateLotForm):
                lot_pk = form_data.get('private_lot-lots')

            elif isinstance(form, forms.LotsForm):
                lot_pk = form_data.get('lot-lots')

            if not lot_pk:
                raise InvalidStateStepError(
                    'Não foi possivel pegar uma referencia de lote.'
                )

            # persistir lote selecionado para ser usado posteriormente.
            self.request.session['lot_pk'] = lot_pk
            subscription = self.get_subscription()
            subscription.lot_id = lot_pk
            subscription.save()

        # Persisting person
        if isinstance(form, forms.SubscriptionPersonForm):
            if not form.is_valid():
                raise ValidationError(form.errors)

            self.person = form.save()

        # Persisting survey
        if isinstance(form, forms.SurveyForm):

            survey_director = SurveyDirector(event=self.event,
                                             user=self.request.user)

            lot = self.get_lot()

            survey_response = QueryDict('', mutable=True)
            for form_question, form_response in form_data.items():
                if form_question == 'csrfmiddlewaretoken':
                    survey_response.update({form_question: form_response})

                if 'survey-' in form_question:
                    survey_response.update(
                        {form_question.replace('survey-', ''): form_response})

            survey_form = survey_director.get_form(
                survey=lot.event_survey.survey,
                data=survey_response
            )

            if survey_form.is_valid():
                survey_form.save_answers()
            else:
                raise Exception('SurveyForm was invalid: {}'.format(
                    survey_form.errors
                ))

        # Persisting payments:
        if isinstance(form, forms.PaymentForm):

            if not form.is_valid():
                raise ValidationError(form.errors)

            try:
                form.save()

            # except DebtAlreadyPaid as e:
            #     raise ValidationError(str(e))

            except TransactionError as e:
                raise ValidationError(str(e))

        return form_data

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context['remove_preloader'] = True
        context['event'] = self.event
        context['is_private_event'] = self.is_private_event()
        context['num_lots'] = self.get_num_lots()
        context['subscription'] = self.get_subscription()
        context['is_last'] = self.steps.current == self.steps.last

        has_open_boleto = False

        if self.storage.current_step not in ['lot', 'private_lot']:
            lot = self.get_lot()
            context['selected_lot'] = lot

            opened_boletos = self.get_open_boleto(lot=lot)
            has_open_boleto = \
                opened_boletos.count() > 0 if opened_boletos else False

        context['has_open_boleto'] = has_open_boleto

        if self.storage.current_step == 'private_lot':
            code = self.request.session.get('exhibition_code')
            if self.is_valid_exhibition_code(code):
                lots = Lot.objects.filter(
                    private=True,
                    exhibition_code=code.upper()
                )
                if lots:
                    context['lot'] = lots.first()

        if self.storage.current_step == 'lot':
            context['has_coupon'] = self.has_coupon()

        if self.storage.current_step == 'person':

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

        if self.storage.current_step == 'payment':
            context['pagarme_encryption_key'] = settings.PAGARME_ENCRYPTION_KEY
            context['lot'] = self.get_lot()

            allowed_types = [Transaction.CREDIT_CARD]

            if is_boleto_allowed(self.event) and has_open_boleto is False:
                allowed_types.append(Transaction.BOLETO)

            context['allowed_transaction_types'] = ','.join(allowed_types)

            subscription = self.get_subscription()
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

        if 'has_private_subscription' in self.request.session:
            del self.request.session['has_private_subscription']

        subscription = self.get_subscription()
        subscription.lot = self.get_lot()

        with atomic():
            try:
                subscription.completed = True
                subscription.save()

                new_account = self.request.user.last_login is None

                if subscription.free is True:
                    subscription.status = Subscription.CONFIRMED_STATUS
                    subscription.save()

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

                    success_url = reverse_lazy('public:hotsite', kwargs={
                        'slug': self.event.slug,
                    })

                else:
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
                        'public:hotsite-subscription-status',
                        kwargs={'slug': self.event.slug, }
                    )

                self.clear_session()

                messages.success(self.request, msg)
                return redirect(success_url)

            except Exception as e:
                self.clear_session()

                raise InvalidStateStepError('Algum erro ocorreu: {}'.format(e))

    def clear_string(self, field_name, data):
        if data and field_name in data:

            value = data.get(field_name)

            if value:
                value = value \
                    .replace('.', '') \
                    .replace('-', '') \
                    .replace('/', '') \
                    .replace('(', '') \
                    .replace(')', '') \
                    .replace(' ', '')

                data[field_name] = value

        return data

    def has_paid_lots(self):
        """ Retorna se evento possui algum lote pago. """
        for lot in self.event.lots.all():
            if lot.price and lot.price > 0:
                return True

        return False

    def has_coupon(self):
        """ Retorna se possui cupon, seja qual for. """
        for lot in self.event.lots.all():
            # código de exibição
            if lot.status == lot.LOT_STATUS_RUNNING and \
                    lot.private and \
                    lot.exhibition_code:
                return True

        return False

    def is_private_event(self):
        """ Verifica se evento é privado possuindo apenas lotes privados. """
        public_lots = []
        private_lots = []

        for lot in self.event.lots.all():
            if lot.private is True:
                private_lots.append(lot.pk)
                continue

            if self.is_lot_available(lot):
                public_lots.append(lot.pk)

        return len(public_lots) == 0 and len(private_lots) > 0

    def is_valid_exhibition_code(self, code):
        """
        Verifica se código de exibição informado é válido para o evento.
        """
        if code:
            for lot in self.event.lots.filter(private=True):
                running = lot.status == lot.LOT_STATUS_RUNNING
                if lot.exhibition_code.upper() == code.upper() and running:
                    return True

        return False

    def has_previous_valid_code(self):
        """
        Verifica se código de exibição previamente enviado na sessão é válido.
        """
        if 'exhibition_code' not in self.request.session:
            return False

        code = self.request.session.get('exhibition_code')
        return self.is_valid_exhibition_code(code)

    def clear_session_exhibition_code(self):
        if 'exhibition_code' not in self.request.session:
            return

        del self.request.session['exhibition_code']

    def clear_session(self):
        def remove_session_key(key):
            if key in self.request.session:
                del self.request.session[key]

        self.clear_session_exhibition_code()
        remove_session_key('has_private_subscription')
        remove_session_key('lot_pk')

    def get_person_from_session(self):
        if not self.person:
            try:
                self.person = Person.objects.get(user=self.request.user)

            except Person.DoesNotExist:
                raise InvalidStateStepError(
                    'Usuário não possui pessoa vinculada.'
                )

        return self.person

    def get_lot(self):
        if 'lot_pk' in self.request.session:
            # se PK de lote existe na sessão, prioriza-lo pois ele pode
            # ser um lote vindo do primeiro passo.
            try:
                return Lot.objects.get(pk=self.request.session['lot_pk'])

            except Lot.DoesNotExist:
                raise InvalidStateStepError(
                    'Lote com pk "pk" não encontrado.'.format(
                        self.request.session['lot_pk']
                    )
                )

        # se não há PK de lote, vamos verificar se usuário já possui inscrição
        subscription = self.get_subscription()

        if subscription.lot is not None:
            # Se inscrição é nova, ou seja, não possui lote, voltar.
            raise InvalidStateStepError(
                'Usuário sem inscrição e lote selecionado.'
            )

        # se inscrição já existia anteriormente, vamos fixar como lote
        # selecionado o lote da inscrição, que pode ser mudado caso o usurio
        # vá para o primeiro passo de seleção de lote.
        self.request.session['lot_pk'] = subscription.lot.pk
        return subscription.lot

    def get_subscription(self):
        if not self.subscription:
            person = self.get_person_from_session()

            try:
                self.subscription = Subscription.objects.get(
                    person=person,
                    event=self.event
                )
                self.subscription.is_new = self.subscription.completed

            except Subscription.DoesNotExist:
                self.subscription = Subscription(
                    person=person,
                    event=self.event,
                    completed=False,
                    created_by=self.request.user.pk
                )
                self.subscription.is_new = self.subscription.completed

        return self.subscription

    def get_num_lots(self):
        lots = [
            lot
            for lot in self.event.lots.all()
            if lot.status == lot.LOT_STATUS_RUNNING
        ]
        return len(lots)

    def get_open_boleto(self, lot):
        return get_opened_boleto_transactions(self.get_subscription())

    def has_paid_subscription(self):
        subscription = self.get_subscription()
        return subscription.transactions.filter(
            status=Transaction.PAID
        ).count() > 0

    @staticmethod
    def is_lot_available(lot):
        return lot.status == lot.LOT_STATUS_RUNNING and not lot.private

    def subscription_enabled(self):

        if self.has_available_lots() is False:
            return False

        return self.event.status == Event.EVENT_STATUS_NOT_STARTED

    def has_available_lots(self):
        available_lots = []

        for lot in self.event.lots.filter(active=True):
            if lot.status == lot.LOT_STATUS_RUNNING:
                available_lots.append(lot)

        return True if len(available_lots) > 0 else False
