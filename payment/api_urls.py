# pylint: skip-file
from django.conf.urls import url
from rest_framework import routers

from payment import viewsets
from payment.views import postback_url_view

router = routers.DefaultRouter()

router.register(r'payer/benefactors',
                viewsets.BenefactorViewSet,
                base_name='benefactor')

router.register(r'payment/transactions',
                viewsets.TransactionReadOnlyViewSet,
                base_name="transactions", )

api_single_endpoints = [
    url(r'^payment/transactions/(?P<pk>[\d]+)/statuses/',
        viewsets.TransactionStatusListView.as_view(),
        name='transactions-statuses'),
    url(r'^payment/checkout/',
        viewsets.SubscriptionCheckoutView.as_view(),
        name='checkout'),
]

public_payment_api_urls = [
    url(
        r'pagarme/postback/'
        '(?P<uidb64>[0-9A-Za-z_\-]+)/$',
        postback_url_view,
        name='payment_postback_url'
    ),
]

urlpatterns = router.urls
urlpatterns += public_payment_api_urls
urlpatterns += api_single_endpoints
