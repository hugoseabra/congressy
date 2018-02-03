from django.conf.urls import include, url

from .views import postback_url_view

public_payment_urls = [
    url(
        r'pagarme/postback/'
        '(?P<uidb64>[0-9A-Za-z_\-]+)/$',
        postback_url_view,
        name='payment_postback_url'
    ),
]


urlpatterns_public_account = [url(r'^', include(public_payment_urls))]

