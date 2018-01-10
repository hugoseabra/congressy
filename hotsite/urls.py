""" Urls do hotsite """
from django.conf.urls import include, url

from . import views

public_hotsite_urls = [
    url(r'^(?P<slug>[\w-]+)/$', views.HotsiteView.as_view(), name='hotsite'),
    url(r'^(?P<slug>[\w-]+)/form/$', views.HotsiteView.as_view(), name='hotsite-form'),
]

urlpatterns_public_hotsite = [url(r'^', include(public_hotsite_urls))]
