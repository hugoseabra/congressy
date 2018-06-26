from django.contrib import messages
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import generic

from core.views.mixins import TemplateNameableMixin
from gatheros_event.helpers.account import update_account
from gatheros_event.models import Event
from gatheros_event.views.mixins import AccountMixin
from gatheros_subscription.forms import EventSurveyForm, FormConfigForm
from gatheros_subscription.models import EventSurvey


class EventViewMixin(AccountMixin, generic.View):
    """ Mixin de view para vincular com informações de event. """
    event = None

    def dispatch(self, request, *args, **kwargs):
        event = self.get_event()

        update_account(
            request=self.request,
            organization=event.organization,
            force=True
        )

        self.permission_denied_url = reverse(
            'event:event-panel',
            kwargs={'pk': self.kwargs.get('event_pk')}
        )
        return super(EventViewMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # noinspection PyUnresolvedReferences
        context = super(EventViewMixin, self).get_context_data(**kwargs)
        context['event'] = self.get_event()
        context['has_paid_lots'] = self.has_paid_lots()

        return context

    def get_event(self):
        """ Resgata organização do contexto da view. """

        if self.event:
            return self.event

        self.event = get_object_or_404(
            Event,
            pk=self.kwargs.get('event_pk')
        )
        return self.event

    def has_paid_lots(self):
        """ Retorna se evento possui algum lote pago. """
        for lot in self.event.lots.all():

            price = lot.price

            if price and price > 0:
                return True

        return False

    def can_access(self):
        return self.get_event().organization == self.organization

    def get_permission_denied_url(self):
        return reverse('event:event-list')


class FormConfigView(TemplateNameableMixin, EventViewMixin, generic.FormView):
    """ Formulário de configuração de inscrição."""

    form_class = FormConfigForm
    template_name = 'subscription/form_config.html'
    object = None

    def dispatch(self, request, *args, **kwargs):
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

        if self.has_paid_lots():
            initial.update({
                'email': True,
                'phone': True,
                'city': True,
                'cpf': FormConfigForm.Meta.model.CPF_REQUIRED,
                'birth_date': FormConfigForm.Meta.model.BIRTH_DATE_REQUIRED,
                'address': FormConfigForm.Meta.model.ADDRESS_SHOW,
            })

        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['event'] = self.get_event()
        kwargs['has_paid_lots'] = self.has_paid_lots()

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
        cxt['event_survey_list'] = self._get_event_surveys()
        cxt['survey_list_form'] = EventSurveyForm(event=self.event)

        return cxt

    def _get_event_surveys(self):

        survey_list = []
        all_surveys = EventSurvey.objects.all().filter(
            event=self.event).order_by(Lower('survey__name'))

        for event_survey in all_surveys:
            lots = event_survey.lots.all().order_by(Lower('name'))
            survey_list.append({
                'event_survey': event_survey,
                'lots': list(lots),
            })

        return survey_list


