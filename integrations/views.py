from django.views.generic import FormView, TemplateView

from gatheros_event.views.mixins import EventViewMixin
from .forms import MailChimpIntegrationForm


class EventIntegrationsView(EventViewMixin, TemplateView):
    form_class = MailChimpIntegrationForm
    template_name = 'integrations/index.html'

    def can_access(self):
        can = super().can_access()
        feature_active = self.event.feature_management.integrations is True

        return can is True and feature_active is True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['has_inside_bar'] = True
        context['active'] = 'integrations'

        return context


class MailChimpIntegrationsView(EventViewMixin, FormView):
    form_class = MailChimpIntegrationForm
    template_name = 'integrations/mailchimp.html'

    def __init__(self, *args, **kwargs):
        self.integration = None
        super().__init__(*args, **kwargs)

    def get_integration(self):
        if self.integration:
            return self.integration

        if hasattr(self.event, 'mailchimp_integration') is False:
            return None

        self.integration = self.event.mailchimp_integration

        return self.integration

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        integration = self.get_integration()
        if integration:
            kwargs.update({
                'instance': integration
            })

        return kwargs

    def can_access(self):
        can = super().can_access()
        feature_active = self.event.feature_management.integrations is True

        return can is True and feature_active is True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['integration'] = self.get_integration()

        return context

