""" Urls do hotsite """
from django.conf.urls import include, url

from . import views

public_hotsite_urls = [
    url(r'^hotsite$', views.hotsite_base, name='hotsite_base'),
    url(r'^hotsite-form$', views.hotsite_form, name='hotsite_form'),
]

urlpatterns_public_hotsite = [url(r'^', include(public_hotsite_urls))]
