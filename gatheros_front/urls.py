from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    url(r'^entrar/$', auth_views.LoginView.as_view(template_name='gatheros_front/login.html'),
        name='login'),

    url(r'^sair/$', auth_views.LogoutView.as_view(), name='logout'),

    url(r'^inicio/$', views.Start.as_view(), name='start'),
    url(r'^$', views.Home.as_view(), name='home'),

]


