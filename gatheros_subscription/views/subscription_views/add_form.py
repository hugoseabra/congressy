from django.contrib import messages
from django.db.transaction import atomic
from django.shortcuts import redirect
from django.urls import reverse

from core.forms.cleaners import clear_string
from gatheros_subscription.directors import SubscriptionSurveyDirector
from gatheros_subscription.models import (
    Lot,
)
from gatheros_subscription.views import SubscriptionFormMixin
from payment import forms
from payment.models import Transaction


class SubscriptionAddFormView(SubscriptionFormMixin):
    """ Formulário de inscrição """
    success_message = 'Inscrição criada com sucesso.'

    def get_success_url(self):
        if self.success_message:
            messages.success(self.request, self.success_message)

        if not self.subscription.free:
            return reverse('subscription:subscription-payments', kwargs={
                'event_pk': self.event.pk,
                'pk': self.subscription.pk,
            })

        return reverse('subscription:subscription-view', kwargs={
            'event_pk': self.event.pk,
            'pk': self.subscription.pk,
        })

    def get_error_url(self):
        return reverse('subscription:subscription-add', kwargs={
            'event_pk': self.event.pk
        })

    def get_context_data(self, **kwargs):

        survey_form = kwargs.pop('survey_form', None)

        future_status = Lot.LOT_STATUS_NOT_STARTED
        finished_status = Lot.LOT_STATUS_FINISHED
        running_status = Lot.LOT_STATUS_RUNNING

        context = super().get_context_data(**kwargs)
        context['running_lots'] = \
            self._get_lots_with_status(running_status)
        context['stopped_lots'] = \
            self._get_lots_with_status(finished_status)
        context['future_lots'] = \
            self._get_lots_with_status(future_status)

        if context['selected_lot'] != 0:
            try:

                lot_pk = context['selected_lot']

                lot = Lot.objects.get(pk=lot_pk)
                if lot.event_survey:
                    if survey_form:
                        context['survey_form'] = survey_form
                    else:
                        survey = lot.event_survey.survey
                        context['survey_form'] = self.get_survey_form(survey)
            except Lot.DoesNotExist:
                pass

        return context

    def post(self, request, *args, **kwargs):
        """
            Handles POST requests, instantiating a form instance with the passed
            POST variables and then checked for validity.
        """
        if self.allow_edit_lot and 'subscription-lot' not in request.POST:
            messages.warning(request, 'Você deve informar um lote.')
            return redirect(self.get_error_url())

        request.POST = request.POST.copy()

        to_be_pre_cleaned = [
            'person-cpf',
            'person-phone',
            'person-zip_code',
            'person-institution_cnpj'
        ]

        for field in to_be_pre_cleaned:
            if field in request.POST:
                request.POST[field] = clear_string(request.POST[field])

        form = self.get_form()
        if form.is_valid():

            lot_pk = self.request.POST.get('subscription-lot')
            if not lot_pk:
                lot_pk = self.subscription.lot.pk

            with atomic():
                self.object = form.save()
                subscription_form = self.get_subscription_form(
                    person=self.object,
                    lot_pk=lot_pk,
                )
                if not subscription_form.is_valid():

                    for name, error in subscription_form.errors.items():
                        form.add_error(field='__all__', error=error[0])

                    return self.form_invalid(form)

                self.subscription = subscription_form.save()

                survey_form = None
                if self.subscription.lot.event_survey:

                    survey = self.subscription.lot.event_survey.survey

                    survey_form = self.get_survey_form(
                        survey=survey,
                        data=self.request.POST,
                        files=self.request.FILES,
                        subscription=self.subscription,
                    )

                    if survey_form.is_valid():
                        survey_form.save()
                    else:
                        return self.form_invalid(form, survey_form=survey_form)

                # Criação de Transaction caso seja pago
                trans_type = Transaction.MANUAL_WAITING_PAYMENT
                trans_form = forms.ManualTransactionForm(
                    subscription=self.subscription,
                    data={
                        'manual_author': '{} ({})'.format(
                            request.user.get_full_name(),
                            request.user.email,
                        ),
                        'paid': False,
                        'manual_payment_type': trans_type,
                        'amount': self.subscription.lot.get_calculated_price()
                    }
                )
                if not trans_form.is_valid():
                    return self.form_invalid(form, survey_form=survey_form)

                trans_form.save()
                return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form, survey_form=None):
        """
        If the form is invalid, re-render the context data with the
        data-filled form and errors.
        """
        return self.render_to_response(
            self.get_context_data(form=form, survey_form=survey_form))

    def get_survey_form(self, survey, subscription=None, data=None,
                        files=None):

        survey_director = SubscriptionSurveyDirector(subscription)

        survey_form = survey_director.get_active_form(
            survey=survey,
            data=data,
            files=files,
            update=self.request.method in ['POST', 'PUT'],
        )

        return survey_form

    def _get_lots_with_status(self, status):
        lot_list = list()

        for lot in self.get_lots().filter():
            if lot.status == status:
                lot_list.append(lot)

        return lot_list
