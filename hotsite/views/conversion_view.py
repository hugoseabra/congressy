"""
    View usada para verificar o status da sua inscrição
"""

from django.contrib import messages
from django.shortcuts import reverse, redirect
from django.views import generic

from hotsite.views import SubscriptionFormMixin


class SubscriptionDoneView(SubscriptionFormMixin, generic.TemplateView):
    template_name = 'service_tags/convertion_page.html'

    def __init__(self, **initkwargs):
        self.event = None
        self.subscription = None
        self.next_url = None
        self.conversion_script = None

        super().__init__(**initkwargs)

    def pre_dispatch(self):
        super().pre_dispatch()

        self.event = self.current_event.event
        self.subscription = self.current_subscription.subscription
        self.conversion_script = \
            self.current_event.custom_service_tag.conversion_script

    def dispatch(self, request, *args, **kwargs):

        slug = self.kwargs.get('slug')

        if not slug:
            return redirect('https://congressy.com')

        if not request.user.is_authenticated:
            return redirect('public:hotsite', slug=slug)

        self.pre_dispatch()

        if self.subscription.completed is False:
            messages.error(
                message='Você não possui inscrição neste evento.',
                request=request
            )
            return redirect('public:hotsite', slug=slug)

        conversion_id = None
        if 'conversion_unique_id' in self.request.session:
            conversion_id = self.request.session.get('conversion_unique_id')
            del self.request.session['conversion_unique_id']

        if not conversion_id:
            return redirect('public:hotsite', slug=slug)

        if self.current_subscription.has_transactions():
            if self.conversion_script:
                self.next_url = reverse(
                    'public:hotsite-subscription-status',
                    kwargs={'slug': slug}
                )

            else:
                return redirect(
                    'public:hotsite-subscription-status',
                    slug=slug
                )

        else:
            if self.conversion_script:
                self.next_url = reverse(
                    'public:hotsite',
                    kwargs={'slug': slug}
                )

            else:
                return redirect(
                    'public:hotsite',
                    slug=slug
                )

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['next_url'] = self.next_url
        context['custom_service_tag'] = self.conversion_script
        context['include_tags_path'] = 'service_tags/custom-script-tags.html'
        return context
