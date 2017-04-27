from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class Home(TemplateView):
    template_name = 'gatheros_front/home.html'


class Start(LoginRequiredMixin, TemplateView):
    template_name = 'gatheros_front/start.html'
