from datetime import datetime

from django import forms
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect
from django.views import generic

from gatheros_event.models import Event, Person
from gatheros_subscription.models import Subscription
from hotsite.forms import LotsForm, SubscriptionPersonForm
from hotsite.views.mixins import EventMixin
from hotsite.views.subscription_form_bootstrappers import LotBootstrapper, \
    SubscriptionBootstrapper, EventSurveyBootstrapper, PersonBootstrapper
from hotsite.views.subscription_form_steps import StepOne, StepTwo, \
    StepThree, StepFour, StepFive
from payment.exception import TransactionError
from payment.helpers import PagarmeTransactionInstanceData
from payment.tasks import create_pagarme_transaction
from survey.directors import SurveyDirector


class SubscriptionFormIndexView(EventMixin, generic.View):
    """
        View responsavel por decidir onde se inicia o process de inscrição
    """

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)

        if not request.user.is_authenticated:
            return redirect('public:hotsite', slug=self.event.slug)

        enabled = self.subscription_enabled()
        if not enabled:
            return redirect('public:hotsite', slug=self.event.slug)

        return response

    def get(self, request, *args, **kwargs):

        """
            Se for evento com inscrição por lotes, ir para o step 1,
            caso contrario pode pular direto para o step 2.
        """
        if self.event.subscription_type == Event.SUBSCRIPTION_BY_LOTS:

            step_1 = StepOne(
                request=request,
                event=self.event,
                context={
                    'event': self.event,
                    'remove_preloader': True
                })

            return step_1.render()

        elif self.event.subscription_type == Event.SUBSCRIPTION_SIMPLE:

            lot = self.event.lots.first()

            step_2 = StepTwo(request=request, event=self.event,
                             dependency_artifacts={'lot': lot}, )

            return step_2.render()

    def post(self, request, *args, **kwargs):

        incoming_step = request.POST.get('next_step', 0)
        previous_step = request.POST.get('previous_step', 0)

        if not incoming_step:
            incoming_step = 0

        if not previous_step:
            previous_step = 0

        next_step = int(incoming_step)
        previous_step = int(previous_step)

        if previous_step:

            if previous_step == 1:

                form = LotsForm(event=self.event, data=request.POST)

                if form.is_valid():

                    unbound_form = LotsForm(event=self.event, initial={
                        'coupon_code': form.cleaned_data['coupon_code'],
                        'lots': form.cleaned_data['lots'],
                        'next_step': 1,
                    })

                    step_1 = StepOne(
                        request=request,
                        event=self.event,
                        form=unbound_form,
                        context={
                            'event': self.event,
                            'remove_preloader': True,
                        })

                    return step_1.render()
                else:
                    step_1 = StepOne(
                        request=request,
                        event=self.event,
                        context={
                            'event': self.event,
                            'remove_preloader': True,
                        })

                    return step_1.render()
            elif previous_step == 2:

                person_pk = request.POST.get('person')
                lot_pk = request.POST.get('lot')
                person_bootstrapper = PersonBootstrapper(
                    person_pk=person_pk)
                lot_bootstrapper = LotBootstrapper(lot_pk=lot_pk,
                                                   event=self.event)

                person = person_bootstrapper.retrieve_artifact()
                lot = lot_bootstrapper.retrieve_artifact()

                if person and lot:
                    form = SubscriptionPersonForm(instance=person,
                                                  event=self.event,
                                                  lot=lot,
                                                  initial={
                                                      'next_step': 2,
                                                      'previous_step': 1,
                                                      'lots': lot.pk}
                                                  )

                    step_2 = StepTwo(request=request, event=self.event,
                                     form=form,
                                     dependency_artifacts={'lot': lot})
                    return step_2.render()
                elif lot:
                    step_2 = StepTwo(request=request, event=self.event,
                                     dependency_artifacts={'lot': lot})
                    return step_2.render()

                else:

                    step_1 = StepOne(
                        request=request,
                        event=self.event,
                        context={
                            'event': self.event,
                            'remove_preloader': True,
                        })

                    return step_1.render()

            else:
                return HttpResponseBadRequest()

        else:

            if next_step == 0:

                form = None

                try:
                    person = Person.objects.get(user=self.request.user)
                    subscription = Subscription.objects.get(person=person,
                                                            event=self.event,
                                                            status=Subscription.AWAITING_STATUS)
                    if subscription.lot.date_end < datetime.now():
                        form = LotsForm(event=self.event, initial={
                            'lots': subscription.lot,
                            'next_step': 1,
                        })

                except ObjectDoesNotExist:
                    pass

                step_1 = StepOne(
                    request=request,
                    event=self.event,
                    form=form,
                    context={
                        'event': self.event,
                        'remove_preloader': True
                    })

                return step_1.render()

            elif next_step == 1:

                form = LotsForm(event=self.event, data=request.POST)

                if form.is_valid():
                    lot = form.cleaned_data['lots']
                    coupon_code = form.cleaned_data['coupon_code']

                    form = None

                    try:

                        person = Person.objects.get(user=self.request.user)
                        form = SubscriptionPersonForm(instance=person,
                                                      event=self.event,
                                                      lot=lot,
                                                      initial={
                                                          'next_step': 2,
                                                          'previous_step': 1,
                                                          'coupon_code': coupon_code,
                                                          'lots': lot.pk}
                                                      )
                    except Person.DoesNotExist:
                        pass

                    step_2 = StepTwo(request=request, event=self.event,
                                     form=form,
                                     dependency_artifacts={'lot': lot})

                    return step_2.render()

                # Form did not validate, re-render step #1 and retrieve a lot
                # correctly.

                form = form.initial = {'next_step': 1}
                step_1 = StepOne(
                    request=request,
                    event=self.event,
                    form=form,
                    context={
                        'event': self.event,
                        'remove_preloader': True
                    },
                )

                return step_1.render()

            elif next_step == 2:

                lot_pk = request.POST.get('lots', None)
                lot_bootstrapper = LotBootstrapper(lot_pk=lot_pk,
                                                   event=self.event)
                lot = lot_bootstrapper.retrieve_artifact()

                if not lot:
                    step_1 = StepOne(
                        request=request,
                        event=self.event,
                        context={
                            'event': self.event,
                            'remove_preloader': True
                        })
                    return step_1.render()

                # Pre-form cleaning
                # This is a hack. Please don't do this.
                # Ref: https://stackoverflow.com/questions/12611345/django-why-is-the-request-post-object-immutable
                mutable = self.request.POST._mutable
                self.request.POST._mutable = True

                self.clear_string('cpf')
                self.clear_string('zip_code')
                self.clear_string('phone')
                self.clear_string('institution_cnpj')

                self.request.POST._mutable = mutable

                try:
                    person = Person.objects.get(user=self.request.user)
                    form = SubscriptionPersonForm(instance=person,
                                                  event=self.event,
                                                  data=request.POST,
                                                  lot=lot)
                except Person.DoesNotExist:
                    form = SubscriptionPersonForm(event=self.event,
                                                  lot=lot,
                                                  data=request.POST)

                if form.is_valid():

                    person = form.save()

                    if not person.user:
                        person.user = self.request.user
                        person.save()

                    # try:
                    #     subscription = Subscription.objects.get(
                    #         person=person,
                    #         event=self.event
                    #     )
                    # except Subscription.DoesNotExist:
                    #     subscription = Subscription(
                    #         person=person,
                    #         event=self.event,
                    #         created_by=self.request.user.id
                    #     )
                    #
                    # subscription.lot = lot
                    # subscription.save()

                    """
                        Se o lote possuir surveys, ir para step 3.
                        
                        Se o lote não possuir surveys, e possuir pagamento ir para 
                        step 4
                        
                        Se o lote não possuir surveys, e não possuir pagamento ir 
                        para step 5.
                        
                    """
                    event_survey = lot.event_survey
                    lot_price = lot.price

                    if event_survey:
                        survey_director = SurveyDirector(event=self.event,
                                                         user=self.request.user)

                        survey_form = survey_director.get_form(
                            survey=event_survey.survey)

                        survey_form.fields['next_step'] = forms.IntegerField(
                            initial=3,
                            widget=forms.HiddenInput()
                        )

                        survey_form.fields[
                            'event_survey'] = forms.IntegerField(
                            initial=event_survey.pk,
                            widget=forms.HiddenInput()
                        )

                        survey_form.fields['lot'] = forms.IntegerField(
                            initial=lot.pk,
                            widget=forms.HiddenInput()
                        )

                        survey_form.fields[
                            'previous_step'] = forms.IntegerField(
                            initial=2,
                            widget=forms.HiddenInput()
                        )

                        survey_form.fields['person'] = forms.CharField(
                            initial=str(person.pk),
                            max_length=60,
                            widget=forms.HiddenInput()
                        )

                        # Se o lote possuir surveys, ir para step 3.
                        step_3 = StepThree(request=request, event=self.event,
                                           form=survey_form, lot=lot)

                        return step_3.render()

                    if lot_price > 0:
                        # Se o lote não possuir surveys, e possuir pagamentos ir
                        # para step 4.
                        step_4 = StepFour(request=request, event=self.event,
                                          dependency_artifacts={
                                              'person': person})
                        return step_4.render()

                # Form is not valid, re-render step 2, person form.
                step_2 = StepTwo(request=request, event=self.event,
                                 form=form, dependency_artifacts={'lot': lot})
                return step_2.render()

            elif next_step == 3:

                subscription_pk = request.POST.get('subscription', None)
                lot_pk = request.POST.get('lot', None)
                event_survey_pk = request.POST.get('event_survey', None)

                subscription = None
                event_survey = None
                lot = None

                if subscription_pk:
                    subscription_bootstrapper = SubscriptionBootstrapper(
                        subscription_pk=subscription_pk)
                    subscription = subscription_bootstrapper.retrieve_artifact()

                if event_survey_pk:
                    event_survey_bootstrapper = EventSurveyBootstrapper(
                        event_survey_pk=event_survey_pk)

                    event_survey = event_survey_bootstrapper.retrieve_artifact()
                if lot_pk:
                    lot_bootstrapper = LotBootstrapper(lot_pk=lot_pk,
                                                       event=self.event.pk)

                    lot = lot_bootstrapper.retrieve_artifact()

                if event_survey and subscription and lot:

                    survey_director = SurveyDirector(event=self.event,
                                                     user=self.request.user)
                    form = survey_director.get_form(
                        survey=event_survey.survey,
                        data=request.POST)

                    if form.is_valid():
                        form.save_answers()

                        # Do we have a payments step?
                        if lot.price > 0:
                            step_4 = StepFour(request=request,
                                              event=self.event,
                                              dependency_artifacts={
                                                  'subscription': subscription})
                            return step_4.render()

                        # We don't have a payment step so we can go straight to
                        # step 5
                        step_5 = StepFive(request=request, event=self.event,
                                          dependency_artifacts={
                                              'subscription': subscription})
                        return step_5.render()

                    else:

                        form.fields['next_step'] = forms.IntegerField(
                            initial=3,
                            widget=forms.HiddenInput()
                        )

                        form.fields[
                            'event_survey'] = forms.IntegerField(
                            initial=event_survey,
                            widget=forms.HiddenInput()
                        )

                        form.fields['subscription'] = forms.CharField(
                            initial=str(subscription.pk),
                            max_length=60,
                            widget=forms.HiddenInput()
                        )

                        form.fields[
                            'previous_step'] = forms.IntegerField(
                            initial=2,
                            widget=forms.HiddenInput()
                        )

                        form.fields['lot'] = forms.IntegerField(
                            initial=lot.pk,
                            widget=forms.HiddenInput()
                        )

                        # Form did not validate so we go back to step 3
                        step_3 = StepThree(request=request,
                                           event=self.event,
                                           lot=lot,
                                           form=form)
                        return step_3.render()

                # Missing one of the three required objects so we go back a step
                if lot:
                    step_2 = StepTwo(request=request, event=self.event,
                                     dependency_artifacts={'lot': lot})
                    return step_2.render()

                # Does not have a lot, restart whole process
                step_1 = StepOne(
                    request=request,
                    event=self.event,
                    context={
                        'event': self.event,
                        'remove_preloader': True
                    })
                return step_1.render()

            elif next_step == 4:

                subscription_pk = request.POST.get('subscription', None)
                subscription = None

                lot_pk = request.POST.get('lot', None)
                lot = None

                if subscription_pk:
                    subscription_bootstrapper = SubscriptionBootstrapper(
                        subscription_pk=subscription_pk)
                    subscription = subscription_bootstrapper.retrieve_artifact()
                    lot_pk = subscription.lot.pk

                if lot_pk:
                    lot_bootstrapper = LotBootstrapper(lot_pk=lot_pk,
                                                       event=self.event.pk)

                    lot = lot_bootstrapper.retrieve_artifact()

                if subscription:

                    # if lot needs payments, so we validate if we have some stuff
                    # from step 4.
                    if subscription.lot.price > 0:

                        try:
                            with transaction.atomic():

                                transaction_data = PagarmeTransactionInstanceData(
                                    subscription=subscription,
                                    extra_data=request.POST.copy(),
                                    event=self.event
                                )

                                create_pagarme_transaction(
                                    transaction_data=transaction_data,
                                    subscription=subscription
                                )

                                step_5 = StepFive(request=request,
                                                  event=self.event,
                                                  dependency_artifacts={
                                                      'subscription': subscription})
                                return step_5.render()

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

                                messages.error(request, message=e.message)
                                step_4 = StepFour(request=request,
                                                  event=self.event,
                                                  dependency_artifacts={
                                                      'subscription': subscription})
                                return step_4.render()

                    else:
                        step_5 = StepFive(request=request, event=self.event,
                                          dependency_artifacts={
                                              'subscription': subscription})
                        return step_5.render()

                # Missing one of the required objects so we go back a step
                if lot:
                    step_2 = StepTwo(request=request, event=self.event,
                                     dependency_artifacts={'lot': lot})
                    return step_2.render()

                # Does not have a lot, restart whole process
                step_1 = StepOne(
                    request=request,
                    event=self.event,
                    context={
                        'event': self.event,
                        'remove_preloader': True
                    })
                return step_1.render()

            else:
                return HttpResponseBadRequest()

    def clear_string(self, field_name):

        if field_name not in self.request.POST:
            return

        value = self.request.POST.get(field_name)

        if not value:
            return ''

        value = value \
            .replace('.', '') \
            .replace('-', '') \
            .replace('/', '') \
            .replace('(', '') \
            .replace(')', '') \
            .replace(' ', '')

        self.request.POST[field_name] = value
