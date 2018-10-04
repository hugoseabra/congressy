from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView


class RemarketingRedirectLanding(TemplateView):
    template_name = 'service_tags/redirect_landing.html'
    default_url = reverse_lazy('front:start')

    def __init__(self, **kwargs):
        self.marketing_type = None
        self.page_type = None
        self.next = None
        super().__init__(**kwargs)

    def dispatch(self, request, *args, **kwargs):
        self.marketing_type = request.GET.get('marketing_type')
        self.page_type = request.GET.get('page_type')
        self.next = request.GET.get('next')

        if not self.next:
            self.next = self.default_url

        if settings.DEBUG:
            redirect(self.next)

        if not self.page_type:
            messages.warning(request,
                             "Nenhum tipo de pagina foi informada para "
                             "realizar o redirecionamento!")
            return redirect(self.default_url)

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['marketing_type'] = self.marketing_type
        context['page_type'] = self.page_type
        context['next'] = self.next

        return context
