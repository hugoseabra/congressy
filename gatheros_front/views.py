from django.shortcuts import render
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView



# def home(request, **_):
#     return render(request, 'gatheros_front/home.html', {})


class Home(TemplateView):
    template_name = 'gatheros_front/home.html'