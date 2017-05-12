from django.views.generic import TemplateView

from core.view.user_context import UserContextViewMixin
from gatheros_event.models import Organization


class OrganizationPanelView(UserContextViewMixin, TemplateView):
    template_name = 'gatheros_event/organization/panel.html'

    def get_context_data(self, **kwargs):
        context = super(OrganizationPanelView, self).get_context_data(**kwargs)

        organization = Organization.objects.get(
            pk=self.user_context.active_organization.pk)

        context.update({
            'organization': organization,
            'can_invite': self.request.user.has_perm('gatheros_event.can_invite',
                                                     organization),
        })

        return context

