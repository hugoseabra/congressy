from django.conf.urls import include, url

from .views import postback_url_view, EventPaymentView

public_payment_api_urls = [
    url(
        r'pagarme/postback/'
        '(?P<uidb64>[0-9A-Za-z_\-]+)/$',
        postback_url_view,
        name='payment_postback_url'
    ),
]

private_payment_urls = [
    url(
        r'^(?P<pk>[\d]+)/payments/$',
        EventPaymentView.as_view(),
        name='event-payments'
    ),
]

urlpatterns_private_payments = [url(r'^', include(private_payment_urls))]

urlpatterns_public_payments_api = [url(r'^', include(public_payment_api_urls))]
