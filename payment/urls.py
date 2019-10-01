from django.conf.urls import include, url

from .views import EventPaymentView, CheckoutView

public_payment_urls = [
    url(
        r'^pagarme/checkout/$',
        CheckoutView.as_view(),
        name='payment-checkout'
    ),
]

private_payment_urls = [
    url(
        r'^(?P<pk>[\d]+)/payments/$',
        EventPaymentView.as_view(),
        name='event-payments'
    ),
]

urlpatterns_public_payments = [
    url(r'^', include(public_payment_urls))
]

urlpatterns_private_payments = [
    url(r'^events/(?P<event_pk>[\d]+)/lots/', include(private_payment_urls))
]
