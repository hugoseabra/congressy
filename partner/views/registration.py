from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic import FormView, TemplateView

from partner.forms import FullPartnerRegistrationForm


class RegistrationView(TemplateView, FormView):
    template_name = 'partner/register.html'
    success_url = reverse_lazy('public:partner-registration-done')
    messages = {
        'success': 'Enviamos um email para "{}"'
    }

    def get_form(self, form_class=None):
        return FullPartnerRegistrationForm(
            **self.get_form_kwargs()
        )

    def form_valid(self, form):
        form.save()
        messages.success(self.request, self.messages['success'].format(
            form.cleaned_data.get('email')))
        return redirect(self.success_url)


class RegistrationDoneView(generic.TemplateView):
    template_name = 'partner/registration_done.html'
