from django.contrib import messages
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import generic

from core.util import represents_int
from core.views.mixins import TemplateNameableMixin
from gatheros_event.helpers.event_business import is_paid_event
from gatheros_event.views.mixins import EventViewMixin, EventDraftStateMixin
from gatheros_subscription.forms import EventSurveyForm, FormConfigForm
from gatheros_subscription.models import EventSurvey
from .mixins import SurveyFeatureFlagMixin


class FormConfigView(SurveyFeatureFlagMixin,
                     TemplateNameableMixin,
                     EventViewMixin,
                     generic.FormView,
                     EventDraftStateMixin,):
    """ Formulário de configuração de inscrição."""

    form_class = FormConfigForm
    template_name = 'subscription/form_config.html'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.object = None
        self.event_survey = None

    def dispatch(self, request, *args, **kwargs):

        survey_pk = request.GET.get('survey')

        if survey_pk:
            self.event_survey = get_object_or_404(EventSurvey, pk=survey_pk)

        self.event = self.get_event()
        try:
            self.object = self.event.formconfig
        except AttributeError:
            pass

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('subscription:form-config', kwargs={
            'event_pk': self.kwargs.get('event_pk')
        })

    def get_initial(self):
        initial = super().get_initial()

        is_payable = is_paid_event(self.event)

        if is_payable:
            initial.update({
                'email': True,
                'phone': True,
                'city': True,
                'cpf': FormConfigForm.Meta.model.CPF_REQUIRED is True,
                'birth_date':
                    FormConfigForm.Meta.model.BIRTH_DATE_REQUIRED is True,
                'address': FormConfigForm.Meta.model.ADDRESS_SHOW is True,
            })

        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['event'] = self.get_event()
        self.event = self.get_event()
        if self.object:
            kwargs['instance'] = self.object

        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Dados salvos com sucesso.')
        self.object = form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        cxt = super().get_context_data(**kwargs)

        cxt['has_inside_bar'] = True
        cxt['active'] = 'form-personalizado'
        cxt['object'] = self.object
        cxt['event'] = self.event
        cxt['event_is_payable'] = is_paid_event(self.event)
        cxt['event_survey_list'] = self._get_event_surveys()
        cxt['survey_list_form'] = EventSurveyForm(event=self.event)

        cxt.update(self.get_event_state_context_data(self.event))

        if self.event_survey is not None:
            cxt['survey'] = self.event_survey.survey
            cxt['event_survey'] = self.event_survey

        cxt['tickets'] = self._get_tickets()

        return cxt

    def _get_event_surveys(self):

        survey_list = []
        all_surveys = EventSurvey.objects.all().filter(
            event_id=self.event.pk
        ).order_by(Lower('survey__name'))

        for event_survey in all_surveys:
            tickets = event_survey.tickets.all().order_by(Lower('name'))
            survey_list.append({
                'event_survey': event_survey,
                'tickets': list(tickets),
            })

        return survey_list

    def _get_tickets(self):
        tickets_list = list()
        selected_tickets = list()

        if self.event_survey:

            all_tickets = self.event.tickets.all().order_by(Lower('name'))
            selected_tickets = self.event_survey.tickets.all()

            for ticket in all_tickets:
                tickets_list.append({
                    'ticket': ticket,
                    'selected': ticket in selected_tickets,
                })

        return tickets_list
