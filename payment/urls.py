from django.conf.urls import include, url
from .views import PostBackView

public_payment_urls = [
    url(
        r'pagarme/postback/'
        '(?P<uidb64>[0-9A-Za-z_\-]+)/$',
        PostBackView.as_view(),
        name='payment_postback_url'
    ),
]


urlpatterns_public_account = [url(r'^', include(public_payment_urls))]

