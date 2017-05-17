from django.views.generic import TemplateView

from gatheros_event.views.mixins import AccountMixin

# @TODO Restringir visualização

class OrganizationPanelView(AccountMixin, TemplateView):
    template_name = 'gatheros_event/organization/panel.html'
