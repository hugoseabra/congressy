""" Urls do hotsite """
from django.conf.urls import include, url

from hotsite.views.subscription_form_wizard import FORMS
from . import views

public_hotsite_urls = [
    url(r'^(?P<slug>[\w-]+)/$', views.HotsiteView.as_view(), name='hotsite'),
    url(
        r'^(?P<slug>[\w-]+)/subscription/$',
        views.SubscriptionWizardView.as_view(FORMS),
        name='hotsite-subscription'
    ),
    url(
        r'^(?P<slug>[\w-]+)/subscription/done/$',
        views.SubscriptionDoneView.as_view(),
        name='hotsite-subscription-done'
    ),
    url(
        r'^(?P<slug>[\w-]+)/subscription/status/$',
        views.SubscriptionStatusView.as_view(),
        name='hotsite-subscription-status'
    ),
    url(
        r'^(?P<slug>[\w-]+)/coupon/$',
        views.CouponView.as_view(),
        name='hotsite-coupon'
    ),
    url(
        r'addons/(?P<lot_category_pk>[\d]+)/subscription/(?P<subscription_pk>[0-9A-Fa-f-]+)/products/',
        views.ProductOptionalManagementView.as_view(),
        name='hotsite_products'
    ),
    url(
        r'addons/(?P<lot_category_pk>[\d]+)/subscription/(?P<subscription_pk>[0-9A-Fa-f-]+)/services/',
        views.ServiceOptionalManagementView.as_view(),
        name='hotsite_services'
    ),
]

urlpatterns_public_hotsite = [url(r'^', include(public_hotsite_urls))]
