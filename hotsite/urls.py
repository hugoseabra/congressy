""" Urls do hotsite """
from django.conf.urls import include, url

from . import views

public_hotsite_urls = [
    url(r'^event/(?P<pk>[\d]+)/$', views.HotsiteView.as_view(), name='hotsite'),
]

urlpatterns_public_hotsite = [url(r'^', include(public_hotsite_urls))]
