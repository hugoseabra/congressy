from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.forms import ValidationError
from django.http import HttpResponseRedirect, QueryDict
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import ugettext as _
from formtools.wizard.forms import ManagementForm
from formtools.wizard.views import SessionWizardView

from addon.models import Product
from addon.services import SubscriptionProductService
from gatheros_event.models import Person
from gatheros_subscription.models import Lot, \
    Subscription
from hotsite import forms
from hotsite.views.mixins import EventMixin
from mailer.services import (
    notify_new_free_subscription,
    notify_new_user_and_free_subscription,
)
from payment.exception import TransactionError
from payment.helpers import PagarmeTransactionInstanceData
from payment.tasks import create_pagarme_transaction
from survey.directors import SurveyDirector

FORMS = [("lot", forms.LotsForm),
         ("person", forms.SubscriptionPersonForm),
         ("survey", forms.SurveyForm),
         ("addon", forms.AddonForm),
         ("payment", forms.PaymentForm)]

TEMPLATES = {"lot": "hotsite/lot_form.html",
             "person": "hotsite/person_form.html",
             "survey": "hotsite/survey_form.html",
             "addon": "hotsite/addon_form.html",
             "payment": "hotsite/payment_form.html"
             }


def is_paid_lot(wizard):
    """Return true if user opts for  a paid lot"""

    # Get cleaned data from lots step
    cleaned_data = wizard.get_cleaned_data_for_step('lot') or {'lots': 'none'}

    # Return true if lot has price and price > 0
    lot = cleaned_data['lots']

    if isinstance(lot, Lot):
        if lot.price and lot.price > 0:
            return True

    return False


def has_survey(wizard):
    """ Return true if user opts for a lot with survey"""

    # Get cleaned data from lots step
    cleaned_data = wizard.get_cleaned_data_for_step('lot') or {'lots': 'none'}

    # Return true if lot has price and price > 0
    lot = cleaned_data['lots']

    if isinstance(lot, Lot):

        if lot.event_survey:
            return True

    return False


def has_addons(wizard):
    # Get cleaned data from lots step
    cleaned_data = wizard.get_cleaned_data_for_step('lot') or {'lots': 'none'}

    # Return true if lot has price and price > 0
    lot = cleaned_data['lots']

    if isinstance(lot, Lot):

        if lot.category:
            if lot.category.service_optionals or \
                    lot.category.product_optionals:
                return True

    return False


class SubscriptionWizardView(EventMixin, SessionWizardView):
    condition_dict = {
        'payment': is_paid_lot,
        'survey': has_survey,
        'addon': has_addons
    }

    def dispatch(self, request, *args, **kwargs):

        response = super().dispatch(request, *args, **kwargs)

        if not self.request.user.is_authenticated:
            return redirect('public:hotsite', slug=self.event.slug)

        if not self.storage:
            return redirect('public:hotsite', slug=self.event.slug)

        enabled = self.subscription_enabled()

        if not enabled:
            return redirect('public:hotsite', slug=self.event.slug)

        return response

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

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context['remove_preloader'] = True

        if self.storage.current_step == 'payment':
            context['pagarme_encryption_key'] = settings.PAGARME_ENCRYPTION_KEY

        if self.storage.current_step == 'addon':

            lot_data = self.storage.get_step_data('lot')

            lot = lot_data.get('lot-lots')

            try:
                lot = Lot.objects.get(pk=lot, event=self.event)
            except Lot.DoesNotExist:
                message = 'Não foi possivel resgatar um Lote ' \
                          'a partir das referencias: lot<{}> e evento<{}>.' \
                    .format(lot, self.event)
                raise TypeError(message)

            context['lot_category_pk'] = lot.category.pk

        return context

    def get_form_kwargs(self, step=None):
        kwargs = super().get_form_kwargs(step)

        if step == 'person':
            kwargs.update({'user': self.request.user})

        return kwargs

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def get_form_initial(self, step):

        if step == 'lot':
            return self.initial_dict.get(step, {'event': self.event})
        else:

            lot_data = self.storage.get_step_data('lot')
            if not lot_data:
                # reset the current step to the first step.
                messages.error(
                    self.request,
                    'Por favor escolha um lote.'
                )
                self.storage.current_step = self.steps.first
                return self.render(self.get_form())

            lot = lot_data.get('lot-lots')

            try:
                lot = Lot.objects.get(pk=lot, event=self.event)
            except Lot.DoesNotExist:
                # reset the current step to the first step.
                messages.error(
                    self.request,
                    'Por favor escolha um lote.'
                )
                self.storage.current_step = self.steps.first
                return self.render(self.get_form())

        if step == 'person':
            return self.initial_dict.get(step, {
                'lot': lot,
                'event': self.event,
            })

        if step == 'survey':
            return self.initial_dict.get(step, {
                'event_survey': lot.event_survey,
                'event': self.event,
                'user': self.request.user,
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

            payment_initial = {
                'choosen_lot': lot,
                'event': self.event,
                'person': self.storage.person
            }

            if hasattr(self.storage, 'product_storage'):
                payment_initial.update(
                    {'optional_products': self.storage.product_storage})

            return self.initial_dict.get(step, payment_initial)

        return self.initial_dict.get(step, {})

    def process_step(self, form):

        form_data = self.get_form_step_data(form)

        # Creating a subscription.
        if isinstance(form, forms.LotsForm):

            person = Person.objects.get(user=self.request.user)
            lot = form.cleaned_data.get('lots')

            self.request.session['is_new_subscription'] = False

            try:
                subscription = Subscription.objects.get(
                    person=person,
                    event=self.event
                )
                subscription.lot = lot
                subscription.save()
            except Subscription.DoesNotExist:
                subscription = Subscription.objects.create(
                    person=person,
                    event=self.event,
                    lot=lot,
                    created_by=person.user.pk
                )

                self.request.session['is_new_subscription'] = True

            self.storage.subscription = subscription

        # Persisting person
        if isinstance(form, forms.SubscriptionPersonForm):
            self.storage.person = form.save()
            if not is_paid_lot(self):
                self.set_subscription_as_completed()

        # Persisting survey
        if isinstance(form, forms.SurveyForm):

            survey_director = SurveyDirector(event=self.event,
                                             user=self.request.user)

            lot_data = self.storage.get_step_data('lot')
            lot = lot_data.get('lot-lots')
            try:
                lot = Lot.objects.get(pk=lot, event=self.event)
            except Lot.DoesNotExist:
                message = 'Não foi possivel resgatar um Lote ' \
                          'a partir das referencias: lot<{}> e evento<{}>.' \
                    .format(lot, self.event)
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

                if not is_paid_lot(self):
                    self.set_subscription_as_completed()
            else:
                raise Exception('SurveyForm was invalid: {}'.format(
                    survey_form.errors))

        # Persisting optionals in session storage
        if isinstance(form, forms.AddonForm):

            if not hasattr(self.storage, 'product_storage'):
                self.storage.product_storage = []

            for key, value in form_data.items():
                if 'product_' in key:

                    product = self.get_product(pk=value)

                    if product not in self.storage.product_storage:
                        self.storage.product_storage.append(product)

            if not is_paid_lot(self):
                self.set_subscription_as_completed()

        # Persisting payments:
        if isinstance(form, forms.PaymentForm):

            if form.is_valid():

                # Assert that we have a person in storage
                if not hasattr(self.storage, 'person'):
                    person = Person.objects.get(user=self.request.user)
                    self.storage.person = person

                if not hasattr(self.storage, 'product_storage'):
                    self.storage.product_storage = []

                    addons_data = self.storage.get_step_data('addon')

                    if addons_data:

                        for key, value in addons_data.items():
                            if 'product_' in key:

                                product = self.get_product(pk=value)

                                if product not in self.storage.product_storage:
                                    self.storage.product_storage.append(product)

                if not hasattr(self.storage, 'subscription'):
                    self.storage.subscription = Subscription.objects.get(
                        person=self.storage.person,
                        event=self.event
                    )

                try:
                    with transaction.atomic():

                        transaction_data = PagarmeTransactionInstanceData(
                            subscription=self.storage.subscription,
                            extra_data=form_data,
                            optionals=self.storage.product_storage,
                            event=self.event
                        )

                        create_pagarme_transaction(
                            transaction_data=transaction_data,
                            subscription=self.storage.subscription,
                        )

                        self.storage.subscription.completed = True
                        self.storage.subscription.save()

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

    def done(self, form_list, **kwargs):

        if not hasattr(self.storage, 'subscription'):
            raise Exception('Não possuimos uma subscription '
                            'no storage do wizard')

        subscription = self.storage.subscription
        lot = subscription.lot

        if not hasattr(self.storage, 'product_storage'):
            self.storage.product_storage = []

            addons_data = self.storage.get_step_data('addon')
            if addons_data:
                for key, value in addons_data.items():
                    if 'product_' in key:

                        product = self.get_product(pk=value)

                        if product not in self.storage.product_storage:
                            self.storage.product_storage.append(product)

        if len(self.storage.product_storage) > 0:
            for product in self.storage.product_storage:

                liquid_price = self.get_calculated_price(product.price, lot)

                service = SubscriptionProductService(data={
                    'subscription': subscription.pk,
                    'optional': product.pk,
                    'optional_amount_price': product.price,
                    'optional_liquid_amount': liquid_price,
                })
                
                service.save()

        self.set_subscription_as_completed()

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

    @staticmethod
    def clear_string(field_name, data):
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

    def get_product(self, pk):
        product = None
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            pass

        if not product:
            messages.error(request=self.request,
                           message='Não foi possivel resgatar todos opcionais'
                                   ' selecionados')
            return self.render_goto_step('addon')

        return product

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

    def set_subscription_as_completed(self):

        subscription = self.storage.subscription
        new_subscription = self.request.session['is_new_subscription']

        subscription.completed = True
        new_account = self.request.user.last_login is None
        lot = subscription.lot

        if not lot.price or lot.price == 0:

            subscription.status = Subscription.CONFIRMED_STATUS

            if new_account and new_subscription:
                notify_new_user_and_free_subscription(self.event, subscription)
            else:
                notify_new_free_subscription(self.event, subscription)

        subscription.save()

