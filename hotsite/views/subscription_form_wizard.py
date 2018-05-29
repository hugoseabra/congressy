from datetime import datetime, timedelta
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import transaction
from django.forms import ValidationError
from django.http import QueryDict
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import ugettext as _
from formtools.wizard.forms import ManagementForm
from formtools.wizard.views import SessionWizardView

from addon.models import SubscriptionProduct, SubscriptionService
from gatheros_event.models import Person, Event
from gatheros_subscription.models import FormConfig, Lot, Subscription
from hotsite import forms
from mailer.services import (
    notify_new_free_subscription,
    notify_new_user_and_free_subscription,
)
from payment.exception import TransactionError
from payment.helpers import PagarmeTransactionInstanceData
from payment.models import Transaction
from payment.tasks import create_pagarme_transaction
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


def has_payments(wizard):
    """Return true if user opts for  a paid lot"""

    # Get cleaned data from lots step
    if is_private_event(wizard):
        cleaned_data = wizard.get_cleaned_data_for_step('private_lot')
    else:
        cleaned_data = wizard.get_cleaned_data_for_step('lot') or \
                       {'lots': 'none'}

    # Return true if lot has price and price > 0
    if cleaned_data:
        lot = cleaned_data['lots']

        if isinstance(lot, Lot):
            if lot.price and lot.price > 0:
                return True

    return False


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
    cleaned_data = wizard.get_cleaned_data_for_step('lot') or {'lots': 'none'}

    # Return true if lot has price and price > 0
    lot = cleaned_data['lots']

    if isinstance(lot, Lot) and lot.category:
        return lot.category.service_optionals.count() > 0

    return False


class SubscriptionWizardView(SessionWizardView):
    condition_dict = {
        'private_lot': is_private_event,
        'lot': is_not_private_event,
        'payment': is_paid_lot,
        'survey': has_survey,
        'service': has_services,
        'product': has_products,
    }
    event = None

    def dispatch(self, request, *args, **kwargs):

        slug = self.kwargs.get('slug')

        if not slug:
            return redirect('https://congressy.com')

        self.event = get_object_or_404(Event, slug=slug)

        user = self.request.user
        if not isinstance(user, User):
            return redirect('public:hotsite', slug=self.event.slug)

        if self.has_paid_subscription():
            messages.warning(
                request,
                "Atenção! Você já possui uma inscrição paga neste evento."
            )
            return redirect(
                'public:hotsite-subscription-status',
                slug=self.event.slug
            )

        if self.is_private_event() and not self.has_previous_valid_code():
            messages.error(
                request,
                "Você deve informar um código válido para se inscrever neste"
                " evento."
            )
            self.clear_session_exhibition_code()
            return redirect('public:hotsite', slug=self.event.slug)

        try:
            return super().dispatch(request, *args, **kwargs)

        except InvalidStateStepError as e:
            print(str(e))

            msg = "Por favor, informe os dados do início para validarmos"
            " as informações de sua inscrição."

            if getattr(settings, 'DEBUG') is True:
                msg += ' Detalhes: ' + str(e)

            messages.warning(request, msg)

            return redirect(
                'public:hotsite-subscription',
                slug=self.event.slug
            )

    def get_form_kwargs(self, step=None):
        kwargs = super().get_form_kwargs(step)

        if step == "private_lot":
            kwargs.update({
                'event': self.event,
                'code': self.request.session.get('exhibition_code')
            })

        if step == 'lot':
            kwargs.update({
                'event': self.event,
            })

        if step == 'person':
            kwargs.update({
                'user': self.request.user,
                'lot': self.get_lot_from_session(),
                'event': self.event,
            })

        if step == 'survey':
            lot_pk = None
            private_lot_data = self.storage.get_step_data('private_lot')
            lot_data = self.storage.get_step_data('lot')

            if private_lot_data is not None:
                lot_pk = private_lot_data.get('private_lot-lots')
            elif lot_data is not None:
                lot_pk = lot_data.get('lot-lots')

            if not lot_pk:
                raise InvalidStateStepError(
                    'Não foi possivel pegar uma referencia de lote.'
                )

            lot = Lot.objects.get(pk=lot_pk, event=self.event)

            kwargs.update({
                'user': self.request.user,
                'event': self.event,
                'event_survey': lot.event_survey,
            })

        if step == 'payment':
            # Assert that we have a person in storage
            if not hasattr(self.storage, 'person'):
                try:
                    person = Person.objects.get(user=self.request.user)
                except Person.DoesNotExist:
                    raise InvalidStateStepError(
                        'User com email {} não possui person'.format(
                            self.request.user.email
                        )
                    )
                self.storage.person = person

            lot_pk = None
            private_lot_data = self.storage.get_step_data('private_lot')
            lot_data = self.storage.get_step_data('lot')

            if private_lot_data is not None:
                lot_pk = private_lot_data.get('private_lot-lots')
            elif lot_data is not None:
                lot_pk = lot_data.get('lot-lots')

            if not lot_pk:
                raise InvalidStateStepError(
                    'Não foi possivel pegar uma referencia de lote.'
                )

            lot = Lot.objects.get(pk=lot_pk, event=self.event)

            kwargs.update({
                'chosen_lot': lot,
                'event': self.event,
                'person': self.storage.person
            })

        return kwargs

    def process_step(self, form):

        form_data = self.get_form_step_data(form)

        # Creating a subscription.
        if isinstance(form, forms.LotsForm) or \
                isinstance(form, forms.PrivateLotForm):

            person = Person.objects.get(user=self.request.user)
            lot = form.cleaned_data.get('lots')

            self.request.session['is_new_subscription'] = False

            try:
                subscription = Subscription.objects.get(
                    person=person,
                    event=self.event
                )
            except Subscription.DoesNotExist:
                subscription = Subscription.objects.create(
                    person=person,
                    event=self.event,
                    lot=lot,
                    completed=False,
                    created_by=person.user.pk
                )

                self.request.session['is_new_subscription'] = True

            self.storage.subscription = subscription
            self.request.session['subscription'] = str(subscription.pk)

            if isinstance(form, forms.PrivateLotForm):
                lot = form_data.get('private_lot-lots')
                self.request.session['lot'] = lot

            if isinstance(form, forms.LotsForm):
                lot = form_data.get('lot-lots')
                self.request.session['lot'] = lot

        # Persisting person
        if isinstance(form, forms.SubscriptionPersonForm):
            person = form.save()
            self.request.session['person'] = str(person.pk)
            self.storage.person = person

        # Persisting survey
        if isinstance(form, forms.SurveyForm):

            survey_director = SurveyDirector(event=self.event,
                                             user=self.request.user)

            lot = self.get_lot_from_session()

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
                    survey_form.errors))

        # Persisting payments:
        if isinstance(form, forms.PaymentForm):

            if form.is_valid():
                # Assert that we have a person in storage
                if not hasattr(self.storage, 'person'):
                    person = Person.objects.get(user=self.request.user)
                    self.storage.person = person

                lot = self.get_lot_from_session()
                subscription = self.get_subscription_from_session()

                try:
                    with transaction.atomic():
                        # Insere ou edita lote
                        subscription.lot = lot
                        subscription.save()

                        transaction_data = PagarmeTransactionInstanceData(
                            subscription=subscription,
                            extra_data=form_data,
                        )

                        create_pagarme_transaction(
                            transaction_data=transaction_data,
                            subscription=subscription
                        )

                except TransactionError as e:
                    error_dict = {
                        'No transaction type': 'Por favor escolher uma forma'
                                               ' de pagamento.',
                        'Transaction type not allowed': 'Forma de pagamento'
                                                        ' não permitida.',
                        'Organization has no bank account': 'Organização não'
                                                            ' está podendo'
                                                            ' receber'
                                                            ' pagamentos no'
                                                            ' momento.',
                        'No organization': 'Evento não possui organizador.',
                    }
                    if e.message in error_dict:
                        e.message = error_dict[e.message]

                    raise ValidationError(e.message)

        return form_data

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context['remove_preloader'] = True
        context['event'] = self.event
        context['is_private_event'] = self.is_private_event()
        context['num_lots'] = self.get_num_lots()

        step = self.storage.current_step

        has_open_boleto = False

        if step not in ['lot', 'private_lot']:
            selected_lot = self.get_lot_from_session()
            context['selected_lot'] = selected_lot

            has_open_boleto = self.get_open_boleto(selected_lot) is not None
            context['has_open_boleto'] = has_open_boleto

        if step == 'private_lot':
            code = self.request.session.get('exhibition_code')
            if self.is_valid_exhibition_code(code):
                lot = Lot.objects.filter(exhibition_code=code.upper())
                if lot:
                    context['lot'] = lot.first()

        if step == 'lot':
            context['has_coupon'] = self.has_coupon()

        if step in ['product', 'service']:
            context['subscription'] = self.get_subscription_from_session()

        if step == 'person':
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

            context['is_last'] = not is_paid_lot(self) and not has_survey(self)

        if step == 'survey':
            context['is_last'] = not is_paid_lot(self)

        if step == 'payment':
            context['pagarme_encryption_key'] = settings.PAGARME_ENCRYPTION_KEY

            subscription = self.get_subscription_from_session()
            context['subscription'] = subscription

            products_queryset = SubscriptionProduct.objects.filter(
                subscription=subscription
            )
            products = [x for x in products_queryset]
            context['products'] = products

            services_queryset = SubscriptionService.objects.filter(
                subscription=subscription
            )
            services = [x for x in services_queryset]
            context['services'] = services

            context['lot'] = subscription.lot

            total = subscription.lot.get_calculated_price() or Decimal(0.00)

            for product in products:
                total += product.optional_price

            for service in services:
                total += service.optional_price

            context['total'] = total

            now = datetime.now()
            days_boleto = timedelta(days=self.event.boleto_limit_days)

            # Data/hora em que os boletos serão desativados.
            diff_days_boleto = now - days_boleto
            boleto_enabled = self.event.date_start >= diff_days_boleto

            payment_types = ['credit_card']

            if boleto_enabled and not has_open_boleto:
                payment_types.append('boleto')

            context['allowed_transaction_types'] = ','.join(payment_types)

        return context

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def done(self, form_list, **kwargs):
        if 'has_private_subscription' in self.request.session:
            del self.request.session['has_private_subscription']

        subscription = self.get_subscription_from_session()
        subscription.completed = True
        subscription.lot = self.get_lot_from_session()
        subscription.save()

        new_account = self.request.user.last_login is None

        if subscription.free is True:
            subscription.status = Subscription.CONFIRMED_STATUS
            subscription.save()

            notified = False
            if new_account and self.request.session['is_new_subscription']:
                notify_new_user_and_free_subscription(self.event, subscription)
                notified = True

            elif self.request.session['is_new_subscription']:
                notify_new_free_subscription(self.event, subscription)
                notified = True

            if notified:
                msg = 'Inscrição realizada com sucesso!' \
                      ' Nós lhe enviamos um e-mail de confirmação de sua' \
                      ' inscrição juntamente com seu voucher.'

            else:
                msg = 'Inscrição salva com sucesso!'

            success_url = reverse_lazy('public:hotsite', kwargs={
                'slug': self.event.slug,
            })

        else:
            if self.request.session['is_new_subscription']:
                msg = 'Inscrição realizada com sucesso!' \
                      ' Nós lhe enviamos um e-mail de confirmação de' \
                      ' sua inscrição. Porém, o seu voucher estará' \
                      ' disponível apenas após a confirmação de seu pagamento.'
            else:
                msg = 'Inscrição salva com sucesso!'

            success_url = reverse_lazy(
                'public:hotsite-subscription-status',
                kwargs={'slug': self.event.slug, }
            )

        self.clear_session()

        messages.success(self.request, msg)
        return redirect(success_url)

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

        wizard_goto_step = self.request.POST.get('wizard_goto_step')
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
        post_data = self.clear_string(
            'person-institution_cnpj',
            data=post_data
        )
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

    def get_subscription_from_session(self):

        if not hasattr(self.storage, 'subscription'):

            if 'subscription' not in self.request.session:
                raise InvalidStateStepError(
                    'Não possuimos uma subscription no storage do wizard'
                )

            subscription_pk = self.request.session['subscription']

            try:
                self.storage.subscription = Subscription.objects.get(
                    pk=subscription_pk
                )

            except Subscription.DoesNotExist:
                raise InvalidStateStepError(
                    'Inscrição salva dentro da session não é valida.'
                )

        return self.storage.subscription

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
            if lot.status == lot.LOT_STATUS_RUNNING and \
                    lot.private and \
                    lot.exhibition_code:
                return True

        return False

    def is_private_event(self):
        """ Verifica se evento é privado possuindo apenas lotes privados. """
        public_lots = []
        private_lots = []

        for lot in self.event.lots.filter():
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

    def has_paid_subscription(self):

        try:
            subscription = self.event.subscriptions.get(
                person__user=self.request.user
            )

            for trans in subscription.transactions.all():
                if trans.status == Transaction.PAID:
                    return True

        except Subscription.DoesNotExist:
            pass

        return False

    def get_person_from_session(self):

        if 'person' not in self.request.session:
            raise InvalidStateStepError('Não temos uma pessoa na session.')

        person_pk = self.request.session['person']

        return Person.objects.get(pk=person_pk)

    def get_lot_from_session(self):

        if 'lot' not in self.request.session:
            raise InvalidStateStepError('Não temos um lote na session.')

        lot_pk = self.request.session['lot']

        return Lot.objects.get(pk=lot_pk)

    def get_num_lots(self):
        lots = [
            lot
            for lot in self.event.lots.all()
            if lot.status == lot.LOT_STATUS_RUNNING
        ]
        return len(lots)

    def get_open_boleto(self, lot):

        now = datetime.now()

        try:
            subscription = self.event.subscriptions.get(
                person__user=self.request.user
            )

            all_transactions = Transaction.objects.filter(
                subscription=subscription,
                lot=lot
            )

            for trans in all_transactions:
                if trans.boleto_expiration_date:
                    if trans.boleto_expiration_date > now.date():
                        return trans

        except Subscription.DoesNotExist:
            pass

        return None

    def clear_session(self):
        keys_to_be_cleared = [
            'subscription',
            'lot',
            'person',
        ]

        for key in keys_to_be_cleared:
            del self.request.session[key]

    def get_calculated_price(self, price, lot):
        """
        Resgata o valor calculado do preço do opcional de acordo com as regras
        da Congressy.
        """
        if price is None:
            return 0

        minimum = Decimal(settings.CONGRESSY_MINIMUM_AMOUNT)
        congressy_plan_percent = \
            Decimal(self.event.congressy_percent) / 100

        congressy_amount = price * congressy_plan_percent
        if congressy_amount < minimum:
            congressy_amount = minimum

        if lot.transfer_tax is True:
            return round(price + congressy_amount, 2)

        return round(price, 2)

    @staticmethod
    def is_lot_available(lot):
        if lot.status == lot.LOT_STATUS_RUNNING and not lot.private:
            return True

        return False
