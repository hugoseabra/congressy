from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.shortcuts import redirect
from django.views.generic import TemplateView

from hotsite.views.mixins import SubscriptionMixin


class BuzzLeadReferralView(SubscriptionMixin, TemplateView):
    template_name = 'hotsite/buzzlead_referral.html'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.campaign = None

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)

        event = self.current_event.event
        subscription = self.current_subscription.subscription

        if subscription.completed is False:
            messages.warning(
                request,
                "Página restrita a participantes."
            )
            return redirect('public:hotsite', slug=event.slug)

        if not event.buzzlead_campaigns.count():
            messages.warning(
                request,
                "Integração de indicação do evento não está ativa. Fale com"
                " o organizador.. "
            )
            return redirect('public:hotsite', slug=event.slug)

        self.campaign = event.buzzlead_campaigns.first()

        if self.campaign.enabled is False:
            messages.warning(
                request,
                "Integração de indicação do evento não está ativa. Fale com"
                " o organizador.. "
            )
            return redirect('public:hotsite', slug=event.slug)

        return response

    def get_context_data(self, **kwargs):
        cxt = super().get_context_data(**kwargs)
        cxt['campaign'] = self.campaign
        cxt['has_top_bar'] = True

        return cxt
