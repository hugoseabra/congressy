from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.shortcuts import redirect
from django.views.generic import TemplateView

from hotsite.views.mixins import SubscriptionMixin


class LiveStreamView(SubscriptionMixin, TemplateView):
    template_name = 'hotsite/live_stream.html'

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)

        event = self.current_event.event
        subscription = self.current_subscription.subscription

        if subscription.confirmed is False:
            messages.warning(
                request,
                "Página restrita a participantes."
            )
            return redirect('public:hotsite', slug=event.slug)

        info = event.info

        if info.enable_streaming_page is False or not info.stream_youtube_code:
            messages.warning(
                request,
                "Página de streaming ao vivo não habilitada. "
            )
            return redirect('public:hotsite', slug=event.slug)

        return response

    def get_context_data(self, **kwargs):
        cxt = super().get_context_data(**kwargs)

        site = Site.objects.get_current()
        cxt['domain'] = '{protocol}://{domain}'.format(
            protocol=getattr(settings, 'ABSOLUTEURI_PROTOCOL', 'http'),
            domain=site.domain,
        )

        cxt['has_top_bar'] = True

        return cxt
