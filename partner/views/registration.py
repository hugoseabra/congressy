from django.urls import reverse_lazy
from django.views import generic

from gatheros_event.views import ProfileCreateView
from partner.forms import PartnerRegistrationForm


class RegistrationView(ProfileCreateView):
    template_name = 'partner/register.html'
    success_url = reverse_lazy('public:partner-registration-done')
    messages = {
        'success': 'Enviamos um email para "%s"'
    }

    def get_form(self, form_class=None):
        return PartnerRegistrationForm(
            **self.get_form_kwargs()
        )


class RegistrationDoneView(generic.TemplateView):
    template_name = 'partner/registration_done.html'
