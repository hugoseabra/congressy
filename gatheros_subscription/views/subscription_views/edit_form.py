from django.contrib import messages
from django.db.transaction import atomic
from django.shortcuts import redirect
from django.urls import reverse

from core.forms.cleaners import clear_string
from gatheros_subscription.directors import SubscriptionSurveyDirector
from gatheros_subscription.views import SubscriptionFormMixin
from ticket.models import Lot


class SubscriptionEditFormView(SubscriptionFormMixin):
    """ Formulário de inscrição """
    success_message = 'Inscrição atualizada com sucesso.'
    allow_edit_lot = False

    def get_success_url(self):
        if self.success_message:
            messages.success(self.request, self.success_message)

        return reverse('subscription:subscription-view', kwargs={
            'event_pk': self.event.pk,
            'pk': self.subscription.pk,
        })

    def get_error_url(self):
        return reverse('subscription:subscription-edit', kwargs={
            'event_pk': self.event.pk,
            'pk': self.subscription.pk,
        })

    def get_context_data(self, **kwargs):

        survey_form = kwargs.pop('survey_form', None)

        context = super().get_context_data(**kwargs)

        tickets = dict()
        for lot in self.get_lots():
            if lot.ticket_id not in tickets:
                tickets[lot.ticket_id] = {
                    'name': lot.name,
                    'lots': list()
                }

            tickets[lot.ticket_id]['lots'].append(lot)

        context['tickets'] = tickets
        if context['selected_lot']:
            try:

                lot_pk = context['selected_lot']

                lot = Lot.objects.get(
                    ticket__event_id=self.event.pk,
                    pk=lot_pk
                )

                ticket = lot.ticket
                context['selected_ticket_name'] = ticket.name

                if ticket.event_survey_id:
                    if survey_form:
                        context['survey_form'] = survey_form
                    else:
                        survey = ticket.event_survey.survey
                        context['survey_form'] = self.get_survey_form(
                            survey,
                            subscription=self.subscription
                        )
            except Lot.DoesNotExist:
                pass

        return context

    def post(self, request, *args, **kwargs):
        """
            Handles POST requests, instantiating a form instance with the passed
            POST variables and then checked for validity.
        """
        if 'subscription-lot' not in request.POST:
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
                lot_pk = self.subscription.ticket_lot_id

            with atomic():
                self.object = form.save()
                subscription_form = self.get_subscription_form(
                    person=self.object,
                    lot_pk=lot_pk,
                )
                if not subscription_form.is_valid():

                    for name, errors in subscription_form.errors.items():
                        for error in errors:
                            form.add_error(field=name, error=error)

                    return self.form_invalid(form)

                self.subscription = subscription_form.save()
                if self.subscription.ticket.event_survey:

                    survey = self.subscription.ticket.event_survey.survey

                    survey_form = self.get_survey_form(
                        survey=survey,
                        data=self.request.POST,
                        files=self.request.FILES,
                        subscription=self.subscription,
                    )

                    if survey_form.is_valid():
                        survey_form.save()
                        return self.form_valid(form)
                    else:
                        return self.form_invalid(form, survey_form=survey_form)

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
