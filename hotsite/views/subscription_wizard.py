from django import forms
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect
from django.views import generic

from gatheros_event.models import Event, Person
from gatheros_subscription.models import Subscription
from hotsite.forms import LotsForm, SubscriptionPersonForm
from hotsite.views.mixins import EventMixin
from hotsite.views.subscription_form_bootstrappers import LotBootstrapper, \
    SubscriptionBootstrapper, EventSurveyBootstrapper
from hotsite.views.subscription_form_steps import StepOne, StepTwo, \
    StepThree, StepFour, StepFive
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

        if not incoming_step:
            incoming_step = 0

        next_step = int(incoming_step)

        if next_step == 0:

            step_1 = StepOne(
                request=request,
                event=self.event,
                context={
                    'event': self.event,
                    'remove_preloader': True
                })

            return step_1.render()

        elif next_step == 1:

            form = LotsForm(event=self.event, data=request.POST)

            if form.is_valid():
                lot = form.cleaned_data['lots']

                form = None

                try:

                    person = Person.objects.get(user=self.request.user)
                    form = SubscriptionPersonForm(instance=person,
                                                  event=self.event,
                                                  lot=lot,
                                                  initial={
                                                      'next_step': 2,
                                                      'lot': lot.pk}
                                                  )
                except Person.DoesNotExist:
                    pass

                step_2 = StepTwo(request=request, event=self.event,
                                 form=form,
                                 dependency_artifacts={'lot': lot})

                return step_2.render()

            # Form did not validate, re-render step #1 and retrieve a lot
            # correctly.
            step_1 = StepOne(
                request=request,
                event=self.event,
                context={
                    'event': self.event,
                    'remove_preloader': True
                },
                form=form,
            )

            return step_1.render()

        elif next_step == 2:

            lot_pk = request.POST.get('lot', None)
            lot_bootstrapper = LotBootstrapper(lot_pk=lot_pk, event=self.event)
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

                try:
                    subscription = Subscription.objects.get(
                        person=person,
                        event=self.event
                    )
                except Subscription.DoesNotExist:
                    subscription = Subscription(
                        person=person,
                        event=self.event,
                        created_by=self.request.user.id
                    )

                subscription.lot = lot
                subscription.save()

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

                    survey_form.fields['event_survey'] = forms.IntegerField(
                        initial=event_survey.pk,
                        widget=forms.HiddenInput()
                    )

                    survey_form.fields['lot'] = forms.IntegerField(
                        initial=lot.pk,
                        widget=forms.HiddenInput()
                    )

                    survey_form.fields['subscription'] = forms.CharField(
                        initial=str(subscription.pk),
                        max_length=60,
                        widget=forms.HiddenInput()
                    )

                    # Se o lote possuir surveys, ir para step 3.
                    step_3 = StepThree(request=request, event=self.event,
                                       form=survey_form)

                    return step_3.render()

                if lot_price > 0:
                    # Se o lote não possuir surveys, e possuir pagamentos ir
                    # para step 4.
                    step_4 = StepFour(request=request, event=self.event,
                                      dependency_artifacts={'subscription':
                                                                subscription})
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
                        step_4 = StepFour(request=request, event=self.event,
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

                    form.fields['lot'] = forms.IntegerField(
                        initial=lot.pk,
                        widget=forms.HiddenInput()
                    )

                    # Form did not validate so we go back to step 3
                    step_3 = StepThree(request=request,
                                       event=self.event,
                                       form=form)
                    step_3.render()

            # Missing one of the three required objects so we go back a step
            if lot:
                step_2 = StepTwo(request=request, event=self.event,
                                 dependency_artifacts={'lot': lot})
                step_2.render()

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
