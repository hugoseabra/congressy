from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    url(r'^entrar/$', views.Login.as_view(), name='login'),
    url(r'^sair/$', auth_views.LogoutView.as_view(), name='logout'),
    url(r'^inicio/$', views.Start.as_view(), name='start'),
    url(r'^$', views.Home.as_view(), name='home'),
]
