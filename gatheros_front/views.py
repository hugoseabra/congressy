from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class Home(TemplateView):
    template_name = 'gatheros_front/home.html'


class Start(LoginRequiredMixin, TemplateView):
    template_name = 'gatheros_front/start.html'


class Login(auth_views.LoginView):
    template_name = 'gatheros_front/login.html'
    redirect_authenticated_user = True
