from django.contrib import messages
from django.urls import reverse
from django.views import generic

from core.views import EventViewMixin
from gatheros_subscription.forms import FormConfigForm


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
