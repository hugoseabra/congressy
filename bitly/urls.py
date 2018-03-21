from django.conf.urls import include, url

from bitly import views

public_bitly_urls = [
    url(
        r'^bitly/$',
        views.BitlyView.as_view(),
        name='bitly'
    ),
]

urlpatterns_public_bitly = [url(r'^', include(public_bitly_urls))]
