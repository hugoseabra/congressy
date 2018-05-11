from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.forms import ValidationError
from django.http import HttpResponseRedirect, QueryDict
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from formtools.wizard.forms import ManagementForm
from formtools.wizard.views import SessionWizardView

from gatheros_event.models import Person, Event
from gatheros_subscription.models import FormConfig, Lot, Subscription
from hotsite import forms
from mailer.services import (
    notify_new_free_subscription,
    notify_new_user_and_free_subscription,
)
from payment.exception import TransactionError
from payment.helpers import PagarmeTransactionInstanceData
from payment.tasks import create_pagarme_transaction
from survey.directors import SurveyDirector

FORMS = [
    ("private_lot", forms.PrivateLotForm),
    ("lot", forms.LotsForm),
    ("person", forms.SubscriptionPersonForm),
    ("survey", forms.SurveyForm),
    ("payment", forms.PaymentForm)
]

TEMPLATES = {
    "private_lot": "hotsite/private_lot_form.html",
    "lot": "hotsite/lot_form.html",
    "person": "hotsite/person_form.html",
    "survey": "hotsite/survey_form.html",
    "payment": "hotsite/payment_form.html"
}


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


def is_private(wizard):
    if wizard.is_private_lot():
        return True

    return False


def is_not_private(wizard):
    if wizard.is_private_lot():
        return False

    return True


class SubscriptionWizardView(SessionWizardView):
    condition_dict = {
        'private_lot': is_private,
        'lot': is_not_private,
        'payment': is_paid_lot,
        'survey': has_survey
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

        if self.is_private_lot() and not self.has_previous_valid_code():
            messages.error(
                request,
                "Você deve informar um código válido para se inscrever neste"
                " evento."
            )
            self.clear_session_exhibition_code()
            return redirect('public:hotsite', slug=self.event.slug)

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context['remove_preloader'] = True
        context['event'] = self.event
        context['is_private'] = self.is_private_lot()

        if self.storage.current_step == 'private_lot':
            code = self.request.session.get('exhibition_code')
            if self.is_valid_exhibition_code(code):
                lot = Lot.objects.filter(
                    exhibition_code=code.upper())
                context['lot'] = lot.first()

        if self.storage.current_step == 'lot':
            context['has_coupon'] = self.has_coupon()

        if self.storage.current_step == 'payment':
            context['pagarme_encryption_key'] = settings.PAGARME_ENCRYPTION_KEY

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

        return context

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def done(self, form_list, **kwargs):

        if 'has_private_subscription' in self.request.session:
            del self.request.session['has_private_subscription']

        if not hasattr(self.storage, 'person'):
            self.storage.person = self.get_person_from_session()

        lot = self.get_lot_from_session()

        new_subscription = False
        new_account = self.request.user.last_login is None

        try:
            subscription = Subscription.objects.get(
                person=self.storage.person,
                event=self.event
            )
        except Subscription.DoesNotExist:
            subscription = Subscription(
                person=self.storage.person,
                event=self.event,
                created_by=self.request.user.id
            )
            new_subscription = True

        # Insere ou edita lote
        subscription.lot = lot
        if not lot.price or lot.price == 0:

            subscription.status = Subscription.CONFIRMED_STATUS

            if new_account and new_subscription:
                notify_new_user_and_free_subscription(self.event, subscription)
            else:
                notify_new_free_subscription(self.event, subscription)

        if 'lot' in self.request.session:
            del self.request.session['lot']

        if 'person' in self.request.session:
            del self.request.session['person']

        subscription.save()

        messages.success(
            self.request,
            'Inscrição realizada com sucesso!'
        )

        if subscription.lot.price and subscription.lot.price > 0:
            return HttpResponseRedirect(reverse_lazy(
                'public:hotsite-subscription-status', kwargs={
                    'slug': self.event.slug,
                }))

        return HttpResponseRedirect(reverse_lazy(
            'public:hotsite', kwargs={
                'slug': self.event.slug,
            }))

    def get_form_initial(self, step):

        if is_private(self):

            if step == "private_lot":
                return self.initial_dict.get(step, {
                    'event': self.event,
                    'code': self.request.session.get('exhibition_code')
                })

        if step == 'lot':
            return self.initial_dict.get(step, {'event': self.event})

        if step == 'survey':
            lot_pk = None
            private_lot_data = self.storage.get_step_data('private_lot')
            lot_data = self.storage.get_step_data('lot')

            if private_lot_data is not None:
                lot_pk = private_lot_data.get('private_lot-lots')
            elif lot_data is not None:
                lot_pk = lot_data.get('lot-lots')

            if not lot_pk:
                raise AttributeError('Não foi possivel pegar uma referencia '
                                     'de lote.')

            lot = Lot.objects.get(pk=lot_pk, event=self.event)

            return self.initial_dict.get(step, {
                'event_survey': lot.event_survey,
            })

        if step == 'payment':
            # Assert that we have a person in storage
            if not hasattr(self.storage, 'person'):

                try:
                    person = Person.objects.get(user=self.request.user)
                except Person.DoesNotExist:
                    raise Exception('User com email {} não possui '
                                    'person'.format(self.request.user.email))

                self.storage.person = person

            lot_pk = None
            private_lot_data = self.storage.get_step_data('private_lot')
            lot_data = self.storage.get_step_data('lot')

            if private_lot_data is not None:
                lot_pk = private_lot_data.get('private_lot-lots')
            elif lot_data is not None:
                lot_pk = lot_data.get('lot-lots')

            if not lot_pk:
                raise AttributeError('Não foi possivel pegar uma referencia '
                                     'de lote.')

            lot = Lot.objects.get(pk=lot_pk, event=self.event)

            return self.initial_dict.get(step, {
                'choosen_lot': lot,
                'event': self.event,
                'person': self.storage.person
            })

        return self.initial_dict.get(step, {})

    def process_step(self, form):

        form_data = self.get_form_step_data(form)

        if isinstance(form, forms.LotsForm) or isinstance(forms.LotsForm):
            lot = form_data.get('lots')
            self.request.session['lot'] = lot.pk

        # Persisting person
        if isinstance(form, forms.SubscriptionPersonForm):
            person = form.save()
            self.request.session['person'] = person.pk
            self.storage.person = person

        # Persisting survey
        if isinstance(form, forms.SurveyForm):

            survey_director = SurveyDirector(event=self.event,
                                             user=self.request.user)

            lot_pk = None
            private_lot_data = self.storage.get_step_data('private_lot')
            lot_data = self.storage.get_step_data('lot')

            if private_lot_data is not None:
                lot_pk = private_lot_data.get('private_lot-lots')
            elif lot_data is not None:
                lot_pk = lot_data.get('lot-lots')

            if not lot_pk:
                raise AttributeError('Não foi possivel pegar uma referencia '
                                     'de lote.')

            try:
                lot = Lot.objects.get(pk=lot_pk, event=self.event)
            except Lot.DoesNotExist:
                message = 'Não foi possivel resgatar um Lote ' \
                          'a partir das referencias: lot<{}> e evento<{}>.' \
                    .format(lot_pk, self.event)
                raise TypeError(message)

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

                try:
                    subscription = Subscription.objects.get(
                        person=self.storage.person,
                        event=self.event
                    )
                except Subscription.DoesNotExist:
                    subscription = Subscription(
                        person=self.storage.person,
                        event=self.event,
                        created_by=self.storage.person.user.id
                    )

                try:
                    with transaction.atomic():
                        # Insere ou edita lote
                        subscription.lot = lot
                        subscription.save()

                        transaction_data = PagarmeTransactionInstanceData(
                            subscription=subscription,
                            extra_data=form_data,
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

                    raise ValidationError(e.message)

        return form_data

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

    def get_form_kwargs(self, step=None):
        kwargs = super().get_form_kwargs(step)

        if step == 'person':

            lot_pk = None
            private_lot_data = self.storage.get_step_data('private_lot')
            lot_data = self.storage.get_step_data('lot')

            if private_lot_data is not None:
                lot_pk = private_lot_data.get('private_lot-lots')
            elif lot_data is not None:
                lot_pk = lot_data.get('lot-lots')

            if not lot_pk:
                raise AttributeError('Não foi possivel pegar uma referencia '
                                     'de lote.')

            lot = Lot.objects.get(pk=lot_pk, event=self.event)

            kwargs.update({'user': self.request.user, 'lot': lot, 'event':
                self.event})

        if step == 'survey':
            kwargs.update({'user': self.request.user, 'event': self.event})

        return kwargs

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

    def is_private_lot(self):
        """ Verifica se evento possui apenas lotes privados. """
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
                if lot.exhibition_code.upper() == code.upper():
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

    def get_person_from_session(self):

        if 'person' not in self.request.session:
            raise Exception('Não temos uma pessoa na session.')

        person_pk = self.request.session['person']

        return Person.objects.get(pk=person_pk)

    def get_lot_from_session(self):

        if 'lot' not in self.request.session:
            raise Exception('Não temos um lote na session.')

        lot_pk = self.request.session['lot']

        return Lot.objects.get(pk=lot_pk)

    @staticmethod
    def is_lot_available(lot):

        if lot.status == lot.LOT_STATUS_RUNNING and not lot.private:
            return True

        return False


