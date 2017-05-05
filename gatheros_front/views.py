from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


# @TODO Colocar collection de Member na sessão do usuário para saber se ele é membro de alguma organização

class Start(LoginRequiredMixin, TemplateView):
    template_name = 'gatheros_front/start.html'


class Login(auth_views.LoginView):
    template_name = 'gatheros_front/login.html'
    redirect_authenticated_user = True
