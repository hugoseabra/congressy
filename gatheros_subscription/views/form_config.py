from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import generic
from django.contrib import messages
from gatheros_event.models import Event
from gatheros_event.views.mixins import (
    AccountMixin,
)
from gatheros_subscription.forms import FormConfigForm


class EventViewMixin(AccountMixin, generic.View):
    """ Mixin de view para vincular com informações de event. """
    event = None

    def dispatch(self, request, *args, **kwargs):
        self.permission_denied_url = reverse(
            'event:event-panel',
            kwargs={'pk': self.kwargs.get('event_pk')}
        )
        return super(EventViewMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # noinspection PyUnresolvedReferences
        context = super(EventViewMixin, self).get_context_data(**kwargs)
        context['event'] = self.get_event()

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


class FormConfigView(EventViewMixin, generic.FormView):
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
        cxt['object'] = self.object

        return cxt
