from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView


class RemarketingRedirectLanding(TemplateView):
    template_name = 'service_tags/redirect_landing.html'
    default_url = reverse_lazy('front:start')
    page_type = None
    next = None

    def dispatch(self, request, *args, **kwargs):
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
        context['page_type'] = self.page_type
        context['next'] = self.next

        return context
