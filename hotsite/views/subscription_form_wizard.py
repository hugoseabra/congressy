from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect, QueryDict
from django.shortcuts import redirect
from django.urls import reverse_lazy
from formtools.wizard.views import SessionWizardView

from gatheros_event.models import Person
from gatheros_subscription.models import Lot, \
    Subscription
from hotsite import forms
from hotsite.views.mixins import EventMixin
from survey.directors import SurveyDirector

FORMS = [("lot", forms.LotsForm),
         ("person", forms.SubscriptionPersonForm),
         ("survey", forms.SurveyForm),
         ("payment", forms.PaymentForm)]

TEMPLATES = {"lot": "hotsite/lot_form.html",
             "person": "hotsite/person_form.html",
             "survey": "hotsite/survey_form.html",
             "payment": "hotsite/payment_form.html"}


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


class SubscriptionWizardView(EventMixin, SessionWizardView):
    condition_dict = {'payment': is_paid_lot, 'survey': has_survey, }

    def dispatch(self, request, *args, **kwargs):

        response = super().dispatch(request, *args, **kwargs)

        if not request.user.is_authenticated:
            return redirect('public:hotsite', slug=self.event.slug)

        enabled = self.subscription_enabled()
        if not enabled:
            return redirect('public:hotsite', slug=self.event.slug)

        return response

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context['remove_preloader'] = True

        if self.storage.current_step == 'payment':
            context['pagarme_encryption_key'] = settings.PAGARME_ENCRYPTION_KEY

        return context

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def done(self, form_list, **kwargs):

        """
          Process non-payment subscriptions here:
            - We have a person in storage.
            - We have the lot data in storage.
            - Survey has already been processed.
        """

        # Assert that we have a person in storage
        if not hasattr(self.storage, 'person'):
            person_data = self.storage.get_step_data('person')
            person_email = person_data.get('person-email')

            person = Person.objects.get(email=person_email)
            self.storage.person = person

        lot_data = self.storage.get_step_data('lot')
        lot = lot_data.get('lot-lots', '')

        # Get a lot object.
        if not isinstance(lot, Lot):
            try:
                lot = Lot.objects.get(pk=lot, event=self.event)
            except Lot.DoesNotExist:
                message = 'Não foi possivel resgatar um Lote ' \
                          'a partir das referencias: lot<{}> e evento<{}>.' \
                    .format(lot, self.event)
                raise TypeError(message)

        subscription = None

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

        # Insere ou edita lote
        subscription.lot = lot
        subscription.save()

        self.storage.subscription = subscription

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

    # this runs for the step it's on as well as for the step before
    def get_form_initial(self, step):

        if step == 'lot':
            return self.initial_dict.get(step, {'event': self.event})

        # get the data for step person from  step lot
        if step == 'person':
            prev_data = self.storage.get_step_data('lot')
            lot = prev_data.get('lot-lots', '')
            return self.initial_dict.get(step, {
                'lot': lot,
                'event': self.event,
                'user': self.request.user,
            })

        # get the data for step survey from  step lot
        if step == 'survey':
            prev_data = self.storage.get_step_data('lot')

            lot = prev_data.get('lot-lots')

            try:
                lot = Lot.objects.get(pk=lot, event=self.event)
            except Lot.DoesNotExist:
                message = 'Não foi possivel resgatar um Lote ' \
                          'a partir das referencias: lot<{}> e evento<{}>.' \
                    .format(lot, self.event)
                raise TypeError(message)

            return self.initial_dict.get(step, {
                'event_survey': lot.event_survey,
                'event': self.event,
                'user': self.request.user,
            })

        if step == 'payment':

            lot_data = self.storage.get_step_data('lot')
            lot = lot_data.get('lot-lots')

            # Assert that we have a person in storage
            if not hasattr(self.storage, 'person'):
                person_data = self.storage.get_step_data('person')
                person_email = person_data.get('person-email')

                person = Person.objects.get(email=person_email)
                self.storage.person = person

            try:
                lot = Lot.objects.get(pk=lot, event=self.event)
            except Lot.DoesNotExist:
                message = 'Não foi possivel resgatar um Lote ' \
                          'a partir das referencias: lot<{}> e evento<{}>.' \
                    .format(lot, self.event)
                raise TypeError(message)

            return self.initial_dict.get(step, {
                'choosen_lot': lot,
                'event': self.event,
                'person': self.storage.person
            })

        return self.initial_dict.get(step, {})

    def process_step(self, form):

        form_data = self.get_form_step_data(form)

        # Persisting person
        if isinstance(form, forms.SubscriptionPersonForm):
            person = form.save()

            if not person.user:
                person.user = self.request.user

            person.save()
            self.storage.person = person

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
            else:
                raise Exception('SurveyForm was invalid: {}'.format(
                    survey_form.errors))

        return form_data
