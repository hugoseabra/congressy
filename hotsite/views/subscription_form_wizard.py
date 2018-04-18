from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from formtools.wizard.views import SessionWizardView

from gatheros_subscription.models import Lot, Subscription
from hotsite import forms
from hotsite.views.mixins import EventMixin

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

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def done(self, form_list, **kwargs):

        """
          Process non-payment subscriptions here:
            - We have a person in storage.
            - We have the lot data in storage.
            - Survey has already been processed.
        """

        # If we already have a subscription in storage, if this is the case,
        # then it was created by the payment step.
        if not hasattr(self.storage, 'subscription'):

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

        subscription = self.storage.subscription

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

        return self.initial_dict.get(step, {})

    def process_step(self, form):

        form_data = self.get_form_step_data(form)

        # Persisting person
        if isinstance(form, forms.SubscriptionPersonForm):
            person = form.save()
            self.storage.person = person

        # Process payment subscriptions here:
        # Create a subscription if the payment works, else re-render the step.

        return form_data
