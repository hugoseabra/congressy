from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


# noinspection PyClassHasNoInit
class Start(LoginRequiredMixin, TemplateView):
    template_name = 'gatheros_front/start.html'


# noinspection PyClassHasNoInit
class Login(auth_views.LoginView):
    template_name = 'auth/login.html'
    redirect_authenticated_user = True
